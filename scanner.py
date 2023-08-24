#!/usr/bin/env python3.11
# scanner.py ver 1.0

import re
import urllib.parse as urlparse

import requests
from rich.console import Console
from bs4 import BeautifulSoup

c = Console()


class Scanner:
    def __init__(self, url, links_to_ignore):
        self.session = requests.Session()
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = links_to_ignore

    def extract_links_from(self, url):
        if ";" in url:
            url = url.replace(";", "")
            c.print(f"Extracted link: {url}")
        try:
            content = self.session.get(url=url).content.decode(errors="ignore")
        except requests.exceptions.ConnectionError as e:
            pass
        else:
            regex = r'(?:href=")(.*?)(?:")'
            return re.findall(regex, content)

    def crawl(self, url=None):
        if url is None:
            url = self.target_url
        href_links = self.extract_links_from(url)
        if href_links:
            for link in href_links:
                link = urlparse.urljoin(base=self.target_url, url=link)

                if "#" in link:
                    link = link.split("#")[0]

                if self.target_url in link:
                    if link not in self.target_links:
                        if link not in self.links_to_ignore:
                            self.target_links.append(link)
                            c.print(f"Crawling link: {link}")
                            self.crawl(link)

    def extract_forms(self, url):
        response = self.session.get(url)
        parsed_html = BeautifulSoup(response.content, features="html.parser")
        return parsed_html.findAll("form")

    def submit_form(self, form, value, url):
        form_name = form.get("name")
        form_action = form.get("action")
        post_url = urlparse.urljoin(url, form_action)
        c.print(f"Form name:\t{form_name}")
        c.print(f"Form action (post url):\t{post_url}")
        form_method = form.get("method")
        c.print(f"Form method:\t\t\t{form_method}")

        inputs_list = form.findAll("input")
        post_data = {}
        for input_field in inputs_list:
            input_name = input_field.get("name")
            input_type = input_field.get("type")
            input_value = input_field.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
            c.print(f"Post data:\t\t{post_data}")
        if form_method == "post":
            return self.session.post(url=post_url, data=post_data)
        return self.session.get(url=post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            form_list = self.extract_forms(link)
            for form in form_list:
                c.print(f"Testing form in: {link}")
                is_vulnerable_to_xss = self.test_xss_in_form(form, link)
                if is_vulnerable_to_xss:
                    c.print(
                        f"\n\nXSS discovered in {link} in the following form:\n\n"
                        f"{form}",
                        style="red bold"
                    )

            if "=" in link:
                c.print(f"Testing: {link}")
                is_vulnerable_to_XSS = self.test_xss_in_links(link)
                if is_vulnerable_to_XSS:
                    c.print(f"\n\nXSS discovered in {link}\n\n", style="red bold")


    def test_xss_in_links(self, url):
        xss_test_script = b"<sCript>alert('test')</scRipt>"
        url = url.replace("=", f"={xss_test_script}")
        response = self.session.get(url)
        return xss_test_script in response.content

    def test_xss_in_form(self, form, url):
        xss_test_script = b"<sCript>alert('test')</scRipt>"
        response = self.submit_form(form, xss_test_script, url)
        return xss_test_script in response.content

