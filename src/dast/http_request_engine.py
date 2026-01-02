import requests


class HttpRequestEngine:
    def __init__(self, token=None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    def get(self, url):
        try:
            return self.session.get(url, timeout=10)
        except:
            return None

    def post(self, url, data=None, json_data=None):
        try:
            if json_data:
                return self.session.post(url, json=json_data, timeout=10)
            return self.session.post(url, data=data, timeout=10)
        except:
            return None
