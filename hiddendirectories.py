#!/usr/bin/env python3
import requests
import re
import sys
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from termcolor import colored

def color_status(code):
    if code == 200:
        return colored(f"{code} OK", "green")
    elif code in [400, 403, 404]:
        return colored(f"{code}", "red")
    elif code in [301, 302]:
        return colored(f"{code} REDIRECT", "blue")
    else:
        return colored(str(code), "yellow")

def extract_data(url):
    try:
        resp = requests.get(url, timeout=10)
        base_url = "{0.scheme}://{0.netloc}".format(requests.utils.urlparse(url))
        soup = BeautifulSoup(resp.text, "html.parser")

        print(colored("\n+ Inline scripts sources:", "cyan", attrs=["bold"]))
        for script in soup.find_all("script"):
            if not script.get("src") and script.string:
                print(colored("[*] Inline JS block", "white"))

        print(colored("\n+ External JS calls:", "cyan", attrs=["bold"]))
        for script in soup.find_all("script", src=True):
            js_url = urljoin(base_url, script["src"])
            try:
                code = requests.get(js_url).status_code
                print(colored(f"[+] Found: {js_url} [{color_status(code)}]", "white"))
            except:
                print(colored(f"[+] Found: {js_url} [ERROR]", "red"))

        print(colored("\n+ CSS, JS, image resources:", "cyan", attrs=["bold"]))
        for tag in soup.find_all(["link", "img"], href=True) + soup.find_all("img", src=True):
            resource = tag.get("href") or tag.get("src")
            full_url = urljoin(base_url, resource)
            try:
                code = requests.get(full_url).status_code
                print(colored(f"[+] Found: {full_url} [{color_status(code)}]", "white"))
            except:
                print(colored(f"[+] Found: {full_url} [ERROR]", "red"))

        print(colored("\n+ Hidden/Interesting endpoints (.php, .asp, etc.):", "cyan", attrs=["bold"]))
        matches = re.findall(r'[\w\-\/]+\.php|\.asp|\.aspx|\.jsp', resp.text, re.IGNORECASE)
        for match in sorted(set(matches)):
            path = urljoin(base_url, match)
            try:
                code = requests.get(path).status_code
                print(colored(f"[+] Found: {path} [{color_status(code)}]", "white"))
            except:
                print(colored(f"[+] Found: {path} [ERROR]", "red"))

        print(colored("\n+ Social media & tracking links:", "cyan", attrs=["bold"]))
        social = re.findall(r'https?://(www\.)?(facebook|twitter|instagram|google|wa\.me)[^\s\'"]+', resp.text)
        for s in set(social):
            full = "https://" + s[1]
            print(colored(f"[+] Found: {full}", "magenta"))

        print(colored("\n+ Phone numbers and tel: links:", "cyan", attrs=["bold"]))
        phones = re.findall(r'(tel:\+?\d{6,15}|\+\d{6,15})', resp.text)
        for phone in set(phones):
            print(colored(f"[+] Found: {phone}", "yellow"))

    except Exception as e:
        print(colored(f"[!] Error fetching {url}: {e}", "red"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HiddenDirectories: Recon tool by Kali-starcyber")
    parser.add_argument("url", help="Target URL to scan")
    args = parser.parse_args()
    extract_data(args.url)
