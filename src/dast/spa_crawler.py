from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json
import time

class SPACrawler:
    def __init__(self, target_url):
        self.target_url = target_url
        self.captured_apis = []
        self.captured_forms = []

    def start(self):
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # --------------------------------------------------
            # NETWORK INTERCEPTION (The "Magic" Part)
            # --------------------------------------------------
            def handle_request(request):
                # We only care about API calls (XHR, Fetch), not images/css
                if request.resource_type in ["xhr", "fetch"]:
                    try:
                        post_data = request.post_data
                        # If data is JSON, parse it; otherwise keep raw
                        if post_data:
                            try:
                                post_data = json.loads(post_data)
                            except:
                                pass
                        
                        self.captured_apis.append({
                            "url": request.url,
                            "method": request.method,
                            "headers": request.headers,
                            "body": post_data
                        })
                    except:
                        pass

            page.on("request", handle_request)

            # --------------------------------------------------
            # NAVIGATION & INTERACTION
            # --------------------------------------------------
            try:
                page.goto(self.target_url, wait_until="networkidle")
                # Wait a bit for extra JS execution
                time.sleep(3) 
                
                # Optional: Scroll to bottom to trigger lazy loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

                # --------------------------------------------------
                # DOM FORM EXTRACTION (After JS executes)
                # --------------------------------------------------
                forms = page.query_selector_all("form")
                for form in forms:
                    action = form.get_attribute("action") or self.target_url
                    method = form.get_attribute("method") or "GET"
                    
                    inputs = []
                    for inp in form.query_selector_all("input, textarea"):
                        name = inp.get_attribute("name")
                        if name:
                            inputs.append(name)

                    if inputs:
                        self.captured_forms.append({
                            "url": urljoin(self.target_url, action),
                            "method": method.upper(),
                            "inputs": inputs
                        })

            except Exception as e:
                print(f"[!] Crawler Error: {e}")

            browser.close()

        # Remove duplicates
        unique_apis = {v['url']: v for v in self.captured_apis}.values()
        return self.captured_forms, list(unique_apis)