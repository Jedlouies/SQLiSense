from colorama import Fore, Style
import datetime


class CLI:
    def banner(self):
        print(Fore.MAGENTA + Style.BRIGHT + """
███████╗ ██████╗ ██╗     ██╗███████╗███████╗███████╗
██╔════╝██╔═══██╗██║     ██║██╔════╝██╔════╝██╔════╝
███████╗██║   ██║██║     ██║███████╗█████╗  ███████╗
╚════██║██║   ██║██║     ██║╚════██║██╔══╝  ╚════██║
███████║╚██████╔╝███████╗██║███████║███████╗███████║
╚══════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚══════╝╚══════╝

        SQLiSense – Generic DAST Scanner
        """)

    def info(self, msg):
        print(Fore.MAGENTA + "[INFO] " + Style.RESET_ALL + msg)

    def success(self, msg):
        print(Fore.GREEN + "[✓] " + Style.RESET_ALL + msg)

    def warn(self, msg):
        print(Fore.YELLOW + "[!] " + Style.RESET_ALL + msg)

    def vuln(self, msg):
        print(Fore.RED + Style.BRIGHT + "[VULNERABLE] " + Style.RESET_ALL + msg)

    def section(self, title):
        print("\n" + Style.BRIGHT + "─" * 45)
        print(title.upper())
        print("─" * 45)

    def summary(self, stats):
        self.section("SCAN SUMMARY")
        print(f"Target            : {stats['target']}")
        print(f"Forms Discovered  : {stats['forms']}")
        print(f"APIs Discovered   : {stats['apis']}")
        print(f"Vulnerabilities   : {stats['vulns']}")
        print(f"High Severity     : {stats['high']}")
        print(f"Medium Severity   : {stats['medium']}")
        print(f"OWASP Categories  : {', '.join(stats['owasp'])}")
        print(f"Scan Time         : {stats['time']}")
        print("Status            : COMPLETED")
        print("─" * 45)
