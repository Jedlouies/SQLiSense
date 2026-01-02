import re
from urllib.parse import urljoin


class APICrawler:
    REGEX = r'["\'](\/api\/[^"\']+|\/rest\/[^"\']+|\/auth\/[^"\']+)["\']'

    def __init__(self, base_url, engine):
        self.base_url = base_url
        self.engine = engine

    def start_scan(self):
        r = self.engine.get(self.base_url)
        if not r:
            return []

        endpoints = set(re.findall(self.REGEX, r.text))
        return [{"url": urljoin(self.base_url, ep)} for ep in endpoints]
