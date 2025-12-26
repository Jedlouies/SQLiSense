import re
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
from typing import Dict, List, Set, Tuple, TypedDict
from .http_request_engine import HttpRequestEngine
import hashlib


class Form(TypedDict):
    url: str
    method: str
    inputs: Dict[str, str]
    origin_url: str

class Crawler:
    """
    A Web Crawler designed for DAST.
    It discovers links and input forms/parameters accross a target website
    """
    def __init__(self, base_url: str, engine: HttpRequestEngine, max_depth: int = 2):
        """
        Initializes the Crawler with a base URL, HTTP request engine, and maximum depth.
        
        :param base_url: The starting URL for the crawler.
        :param engine: An instance of HttpRequestEngine to make HTTP requests.
        :param max_depth: Maximum depth to crawl.
        """
        self.base_url = base_url
        self.engine = engine
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.discovered_forms: List[Form] = []
        self.discovered_form_keys: Set[Tuple[str, str, str]] = set()
        
        
    def _get_absolute_url(self, base: str, link: str) -> str | None:
        """
        Converts a relatve URL to an absolute URL.
        """
        
        link = link.strip()
        
        if link.startswith('#') or link.lower().startswith('javascript:'):
            return None
        
        absolute_url = urljoin(base, link)
        parsed_base = urlparse(self.base_url)
        parsed_link = urlparse(absolute_url)
        
        if parsed_link.scheme not in ('http', 'https'):
            return None
        
        if parsed_link.netloc != parsed_base.netloc:
            return None
        
        normalized_url = parsed_link.scheme + "://" + parsed_link.netloc + parsed_link.path
        return normalized_url.strip('/')
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """
        Extracts all valid links from the HTML soup.
        """
        
        new_links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            abs_url = self._get_absolute_url(current_url, href)
            
            if abs_url and abs_url not in self.visited_urls:
                new_links.add(abs_url)
                
        for script in soup.find_all('script'):
            js_url = re.findall(r'\"(http[s]?://[^\s\"\']*)\"', script.string or '')
            for url in js_url:
                abs_url = self._get_absolute_url(current_url, url)
                if abs_url and abs_url not in self.visited_urls:
                    new_links.add(abs_url)
            
        return new_links
            
    
    def _extract_forms(self, soup: BeautifulSoup, current_url: str):
        """
        Extracts all forms (both <form> tags and standalone input sets) 
        and their input parameters from the HTML soup.
        """
        processed_input_fields = set()
        
        for form_tag in soup.find_all('form'):
            action = form_tag.get('action') or current_url
            target_url = self._get_absolute_url(current_url, action)
            method = form_tag.get('method', 'get').upper()
            
            if not target_url:
                continue
            
            inputs: Dict[str, str] = {}
            for input_tag in form_tag.find_all(['input', 'textarea', 'select']):
                input_name = input_tag.get('name')
                input_type = input_tag.get('type', 'text')
                
                if input_name:
                    inputs[input_name] = input_type
                    # Track input fields inside a form so we don't process them again
                    processed_input_fields.add(input_tag)
                
            form_data: Form = {
                'url': target_url,
                'method': method,
                'inputs': inputs,
                'origin_url': current_url
            }
            
            form_key = (target_url, method)
            
            if form_key not in self.discovered_form_keys: 
                self.discovered_forms.append(form_data)
                self.discovered_form_keys.add(form_key)
                print(f"Discovered FORM tag at {target_url} with method {method} and inputs {inputs}")

        all_inputs = soup.find_all(['input', 'textarea', 'select'])
        
        for input_tag in [tag for tag in all_inputs if tag not in processed_input_fields]:
            if input_tag.get('type') in ('submit', 'button', 'hidden', None):
                continue
            
            inputs: Dict[str, str] = {}
            target_url = current_url
            method = 'POST' 
            parent = input_tag.find_parent()
            if parent:
                for sibling_input in parent.find_all(['input', 'textarea', 'select']):
                    input_name = sibling_input.get('name')
                    input_type = sibling_input.get('type', 'text')
                    if input_name and sibling_input not in processed_input_fields:
                        inputs[input_name] = input_type
                        processed_input_fields.add(sibling_input)
            
            if any(v not in ('hidden', 'submit', 'button') for v in inputs.values()):
                
                pseudo_form_data: Form = {
                    'url': target_url,
                    'method': method,
                    'inputs': inputs,
                    'origin_url': current_url
                }
                
                input_names_sorted = sorted(inputs.keys())
                input_hash = hashlib.sha1(str(input_names_sorted).encode('utf-8')).hexdigest()

                form_key = (target_url, method, input_hash)
                
                if form_key not in self.discovered_form_keys: 
                    self.discovered_forms.append(pseudo_form_data)
                    self.discovered_form_keys.add(form_key)
                    print(f"Discovered PSEUDO-FORM (SPA Fix) at {target_url} with method {method} and inputs {inputs}")
                        
    def crawl(self, url: str, depth: int):
        """
        Recursively crawls the website starting from the given URL up to the specified depth.
        """
        
        if depth > self.max_depth:
            return
        if url in self.visited_urls:
            return
        
        print(f"Crawling URL: {url} at depth {depth}")
        self.visited_urls.add(url)
        
        rendered_html = self.engine.get(url)
        
        if rendered_html is None:
            return
        
        soup = BeautifulSoup(rendered_html, 'html.parser')
        
        self._extract_forms(soup, url)
        
        new_links = self._extract_links(soup, url)
        
        for link in new_links:
            self.crawl(link, depth + 1)
        
        print(f"Completed crawling URL: {url} at depth {depth}")    
        
    def start_scan(self):
        """
        Initializes and runs the crawl process
        """
        
        self.crawl(self.base_url, depth=0)
        return self.discovered_forms
        
    
if __name__ == "__main__":
        
    target_base = 'https://juice-shop.herokuapp.com/#/login'
    
    print("--- Starting DAST Crawler ---")