import argparse
from colorama import init
from src.dast.http_request_engine import HttpRequestEngine
from src.dast.spa_crawler import SPACrawler  # NEW IMPORT
from src.dast.injector import PayloadInjector
from src.dast.cli import CLI
from src.dast.state import ScanState

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True)
    parser.add_argument("--token", help="JWT Bearer Token (optional)")
    args = parser.parse_args()

    cli = CLI()
    cli.banner()

    state = ScanState(args.url)
    engine = HttpRequestEngine(token=args.token)
    injector = PayloadInjector(engine, cli, state)

    cli.info(f"Target       : {args.url}")
    cli.info("Scan Mode    : SPA (Headless Browser) + API Interception")
    
    # --------------------------------------------------
    # PHASE 1: SPA CRAWLING (The Fix)
    # --------------------------------------------------
    cli.section("SPA & API DISCOVERY")
    cli.info("Launching headless browser to intercept traffic...")
    
    crawler = SPACrawler(args.url)
    forms, apis = crawler.start()

    state.forms = len(forms)
    state.apis = len(apis)

    cli.success(f"DOM Forms Found      : {state.forms}")
    cli.success(f"API Calls Captured   : {state.apis}")

    if state.apis > 0:
        cli.info("Captured Endpoints:")
        for api in apis[:5]: # Show first 5
            print(f"   - [{api['method']}] {api['url']}")
        if state.apis > 5: print("   - ... and more")

    # --------------------------------------------------
    # PHASE 2: INJECTION
    # --------------------------------------------------
    
    injector.test_forms(forms)
    injector.test_api(apis)
    injector.test_auth_bypass(apis)

    # FINAL SUMMARY
    cli.summary(state.summary())

if __name__ == "__main__":
    main()