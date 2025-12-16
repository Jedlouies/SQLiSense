import requests
from typing import Optional, Dict, Any 
from playwright.sync_api import sync_playwright, Playwright, Browser, Page

_playwright_context: Optional[Playwright] = None
_browser: Optional[Browser] = None
_page: Optional[Page] = None

def _initialize_playwright_globals():
    """Initializes the single Playwright instance and context."""
    global _playwright_context, _browser, _page
    if _playwright_context is None:
        _playwright_context = sync_playwright().__enter__()
        _browser = _playwright_context.chromium.launch(headless=True)
        _page = _browser.new_page()

def _close_playwright_globals():
    """Closes the Playwright browser and cleans up the context."""
    global _playwright_context, _browser
    if _browser:
        _browser.close()
    if _playwright_context:
        _playwright_context.__exit__(None, None, None)


class HttpRequestEngine:
    """
    Centralized HTTP request engine using Playwright for robust JavaScript rendering (GET)
    and standard requests for attack submissions (POST).
    """

    def __init__(self, timeout: int = 10, headers: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        
        _initialize_playwright_globals()
        
        self.sessions = requests.Session()
        default_headers = {
            "User-Agent": "SQLiSense-DAST/1.0"
        }
        if headers:
            default_headers.update(headers)
        self.sessions.headers.update(default_headers)

    def get(self, url: str):
        """
        Loads the URL using Playwright, executes JavaScript, and returns the 
        fully rendered HTML source string.
        """
        if _page is None:
            print("[FATAL] Playwright page is not initialized.")
            return None
            
        try:
            _page.goto(url, timeout=self.timeout * 1000)
            
            _page.wait_for_load_state("networkidle")

            rendered_html = _page.content()
            return rendered_html
            
        except Exception as e:
            print(f"[HTTP-ERROR] GET {url}: {e}")
            return None
        
    def post(self, url: str, data: Optional[Dict[str, Any]] = None):
        try:
            response = self.sessions.post(
                url,
                data=data,
                timeout=self.timeout,
                allow_redirects=True
            )
            return response
        except requests.RequestException as e:
            print(f"[HTTP-ERROR] POST {url}: {e}")
            return None

    def close(self):
        """
        Closes the Playwright browser and cleans up resources.
        """
        _close_playwright_globals()