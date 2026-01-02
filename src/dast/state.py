import datetime


class ScanState:
    def __init__(self, target):
        self.target = target
        self.forms = 0
        self.apis = 0
        self.vulns = 0
        self.high = 0
        self.medium = 0
        self.owasp = set()
        self.start_time = datetime.datetime.now()

    def add_vuln(self, severity, owasp):
        self.vulns += 1
        self.owasp.add(owasp)
        if severity == "High":
            self.high += 1
        elif severity == "Medium":
            self.medium += 1

    def summary(self):
        end = datetime.datetime.now()
        return {
            "target": self.target,
            "forms": self.forms,
            "apis": self.apis,
            "vulns": self.vulns,
            "high": self.high,
            "medium": self.medium,
            "owasp": list(self.owasp),
            "time": str(end - self.start_time).split(".")[0]
        }
