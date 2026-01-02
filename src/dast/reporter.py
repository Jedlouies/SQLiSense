import csv
import os

class Reporter:
    def __init__(self, filename="scan_report.csv"):
        self.filename = filename
        # Create the file and write headers if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Vulnerability", "URL", "Parameter", "OWASP Category", "Severity"])

    def log(self, vuln_type, url, param, owasp_cat, severity):
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([vuln_type, url, param, owasp_cat, severity])