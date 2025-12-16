
from src.dast.crawler import Crawler
from src.dast.http_request_engine import HttpRequestEngine

def main():
    """
    Entry point for SQLiSense DAST
    Initializes the HTTP Request Engine and Web Crawler.
    """


    target_url = "https://juice-shop.herokuapp.com/#/login"

    print("== SQLiSense ==")
    print(f"Target: {target_url}")

    engine = HttpRequestEngine(
        timeout=10,
        headers={
            "User-Agent": "SQLiSense-DAST/1.0"
        }
    )

    crawler = Crawler(
        base_url=target_url,
        engine=engine,
        max_depth=2
    )

    try:
        discovered_forms = crawler.start_scan()
    finally:
        engine.close()

    print("\n== Scan Complete ==")
    print(f"Total forms discovered: {len(discovered_forms)}")

    for idx, form in enumerate(discovered_forms, start=1):
        print(f"\nForm #{idx}")
        print(f"URL: {form['url']}")
        print(f"Method: {form['method']}")
        print(f"Inputs: {form['inputs']}")

if __name__ == "__main__":
    main()