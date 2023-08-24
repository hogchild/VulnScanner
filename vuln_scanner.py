#!/usr/bin/env python3.11
# vuln_scanner.py ver 1.0

from rich.console import Console
import click
import scanner

c = Console()

target_url = "http://192.168.3.139/"
target_url = "http://192.168.3.139/mutillidae/"
# target_url = "http://192.168.3.139/dvwa/"
# login_url = "http://192.168.3.139/dvwa/login.php"
# links_to_ignore = ["http://192.168.3.139/dvwa/logout.php"]
links_to_ignore = []
# login_data_dict = {
#     "username": "admin",
#     "password": "password",
#     "Login": "submit"
# }

vuln_scanner = scanner.Scanner(target_url, links_to_ignore)
# vuln_scanner.session.post(login_url, login_data_dict)

vuln_scanner.crawl()
# forms = vuln_scanner.extract_forms(url="http://192.168.3.139/dvwa/vulnerabilities/xss_r/")

# vuln_scanner.run_scanner()