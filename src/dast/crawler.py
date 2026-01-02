from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Crawler:
    def __init__(self, base_url, engine):
        self.base_url = base_url
        self.engine = engine

    def start(self):
        r = self.engine.get(self.base_url)
        if not r:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        forms = []

        for form in soup.find_all("form"):
            action = form.get("action") or self.base_url
            method = form.get("method", "post").upper()
            inputs = [i.get("name") for i in form.find_all("input") if i.get("name")]

            if inputs:
                forms.append({
                    "url": urljoin(self.base_url, action),
                    "method": method,
                    "inputs": inputs
                })
        return forms
