import time
import copy
from src.dast.payloads import SQLI_PAYLOADS, AUTH_BYPASS_PAYLOADS
from src.dast.nosql_payloads import NOSQL_JSON_PAYLOADS  # NEW IMPORT
from src.dast.reporter import Reporter
from src.dast.owasp import OWASP_MAPPING


class PayloadInjector:
    def __init__(self, engine, cli, state):
        self.engine = engine
        self.cli = cli
        self.state = state
        self.reporter = Reporter()

    def report_vuln(self, vuln_type, endpoint, param, severity):
        self.cli.vuln(f"{vuln_type} → {endpoint} ({param})")
        self.state.add_vuln(severity, OWASP_MAPPING.get(vuln_type, "Unknown"))
        self.reporter.log(vuln_type, endpoint, param, OWASP_MAPPING.get(vuln_type, "Unknown"), severity)

    # --------------------------------------------------
    # FORM TESTING (SQLi)
    # --------------------------------------------------
    def test_forms(self, forms):
        self.cli.section("FORM SQL INJECTION TESTING")
        if not forms:
            self.cli.warn("No forms to test.")
            return

        for form in forms:
            base_data = {i: "test" for i in form["inputs"]}
            
            if form["method"] == "POST":
                baseline = self.engine.post(form["url"], data=base_data)
            else:
                baseline = self.engine.get(form["url"])

            if not baseline:
                continue

            for field in form["inputs"]:
                for payload in SQLI_PAYLOADS:
                    data = base_data.copy()
                    data[field] = payload

                    start = time.time()
                    if form["method"] == "POST":
                        r = self.engine.post(form["url"], data=data)
                    else:
                        r = self.engine.get(f"{form['url']}?{field}={payload}")
                    
                    delay = time.time() - start

                    if r and (r.text != baseline.text or delay > 2):
                        self.report_vuln("SQL Injection", form["url"], field, "High")
                        break 

    # --------------------------------------------------
    # API TESTING (SQLi)
    # --------------------------------------------------
    def test_api(self, apis):
        self.cli.section("API SQL INJECTION TESTING")
        if not apis:
            self.cli.warn("No APIs to test.")
            return

        for api in apis:
            self._test_single_api_sqli(api)

    def _test_single_api_sqli(self, api):
        url = api["url"]
        original_body = api["body"]

        if api["method"] not in ["POST", "PUT"] or not isinstance(original_body, dict):
            return

        baseline = self.engine.post(url, json_data=original_body)
        if not baseline: return

        for key in original_body.keys():
            for payload in SQLI_PAYLOADS:
                fuzzed_body = copy.deepcopy(original_body)
                fuzzed_body[key] = payload

                start = time.time()
                r = self.engine.post(url, json_data=fuzzed_body)
                delay = time.time() - start

                if r and (delay > 2 or (r.status_code == 500)):
                    self.report_vuln("Blind SQL Injection", url, key, "Medium")
                    break

    # --------------------------------------------------
    # NOSQL INJECTION TESTING (NEW FEATURE)
    # --------------------------------------------------
    def test_nosql_api(self, apis):
        self.cli.section("NoSQL INJECTION TESTING (MongoDB)")
        
        # Filter for likely targets (POST/PUT requests with JSON)
        target_apis = [
            api for api in apis 
            if api["method"] in ["POST", "PUT"] and isinstance(api["body"], dict)
        ]

        if not target_apis:
            self.cli.warn("No suitable APIs for NoSQL testing.")
            return

        for api in target_apis:
            url = api["url"]
            original_body = api["body"]
            self.cli.info(f"Scanning for NoSQLi: {url}")

            # Iterate through every field in the JSON body
            for key in original_body.keys():
                for payload in NOSQL_JSON_PAYLOADS:
                    
                    fuzzed_body = copy.deepcopy(original_body)
                    
                    # Direct Operator Injection
                    # Example: Changes {"user": "admin"} to {"user": {"$ne": null}}
                    fuzzed_body[key] = payload

                    try:
                        r = self.engine.post(url, json_data=fuzzed_body)
                        
                        # DETECTION LOGIC:
                        # 1. Bypass Success: We got a 200 OK and a token/success message
                        # 2. Information Leak: We triggered a database error
                        if r:
                            is_success = r.status_code == 200 and any(k in r.text.lower() for k in ["token", "success", "auth", "id"])
                            is_error = "mongo" in r.text.lower() or "referenceerror" in r.text.lower()

                            if is_success:
                                self.report_vuln("NoSQL Injection (Bypass)", url, key, "Critical")
                                break # Stop fuzzing this key
                            elif is_error:
                                self.report_vuln("NoSQL Injection (Error)", url, key, "Medium")
                                break

                    except Exception as e:
                        print(f"DEBUG: {e}")

    # --------------------------------------------------
    # AUTH BYPASS (Targeted)
    # --------------------------------------------------
    def test_auth_bypass(self, apis):
        self.cli.section("AUTHENTICATION BYPASS TESTING")
        
        login_apis = [
            api for api in apis 
            if any(x in api["url"].lower() for x in ["login", "auth", "signin", "session"])
            and api["method"] == "POST"
        ]

        if not login_apis:
            self.cli.warn("No login endpoints detected.")
            return

        for api in login_apis:
            self.cli.info(f"Attacking Login Endpoint: {api['url']}")
            
            for payload in AUTH_BYPASS_PAYLOADS:
                r = self.engine.post(api["url"], json_data=payload)

                if r and r.status_code == 200 and "token" in r.text.lower():
                    self.report_vuln("Auth Bypass", api["url"], "JSON Body", "Critical")
                    return