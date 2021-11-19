import os
import shutil
import requests
from pathlib import PurePath
from difflib import SequenceMatcher
from colorama.ansi import Back, Fore, Style

class Scanner:
  def __init__(self) -> None:
    self.MIN_DIFF_PERCENTAGE = 70
    self.VULN_LINKS = []
    self.AUTH_HEADER = 'Authorization'
    self.COOKIE_HEADER = 'Cookie'

    self.cwd = f'{os.getcwd()}/'
    self.testing_path = f"{os.getcwd()}/testing_noauth"
    os.system(f"rm -f {self.testing_path}/*")

  def run(self, links_noauth, links_user1, links_user2, links_admin):
    # get diff of links_noauath & links_user1
    diff_links = (list(link for link in links_user1 if link["url"] not in list(link["url"] for link in links_noauth)))
    self.scan_authen_vuln(diff_links)
    print("Authen Vulns:", len(self.VULN_LINKS))

  def scan_authen_vuln(self, links):
    print(Back.GREEN + Fore.BLACK + 'SCANNING FOR VULNERABILITIES...' + Style.RESET_ALL)
    for link in links:
      AUTH_FILES = []
      origin_header = {}
      test_header = {}
      method = ""

      origin_path = self.cwd + link["traffic_file"]

      # r=root, d=directories, f=files
      for r, d, f in os.walk(origin_path):
        for file in f:
          if '.txt' in file:
            url = PurePath(r).name.replace("\\\\", "://")
            os.chdir(r)
            with open(file) as content:
              if self.AUTH_HEADER in content.read() or self.COOKIE_HEADER in content.read():
                shutil.copy(os.path.join(r, file), self.testing_path)
                AUTH_FILES.append({
                  "url": url,
                  "file": file
                })

      os.chdir(self.testing_path)

      for item in AUTH_FILES:
        URL, FILE = item.values()

        with open(FILE, "r") as f_origin:
          lines = f_origin.read().splitlines()

          method = lines[0].split()[0]
          url = URL + lines[0].split()[1]

          for line in lines[1:len(lines) - 1]:
            x = line.split(':', 1)
            origin_header[x[0].strip()] = x[1].strip()

        with open(f"testing_{FILE}", "w") as f_noauth:
          tmp = None
          for line in lines:
            if line.startswith(self.AUTH_HEADER) or line.startswith(self.COOKIE_HEADER):
              tmp = line
            if line != tmp:
              f_noauth.write('{}\n'.format(line))

        with open(f"testing_{FILE}", "r") as f_noauth_r:
          lines_noauth = f_noauth_r.read().splitlines()

          method = lines_noauth[0].split()[0]
          url = URL + lines_noauth[0].split()[1]

          for line in lines_noauth[1:len(lines_noauth) - 1]:
            x = line.split(':', 1)
            test_header[x[0].strip()] = x[1].strip()
        
        if method.lower() == 'get':
          r = requests.get(url, headers=origin_header)
          r2 = requests.get(url, headers=test_header)
        elif method.lower() == 'post':
          r = requests.post(url, headers=origin_header)

        diff_amount = SequenceMatcher(None, r.text, r2.text).ratio() * 100

        if diff_amount > self.MIN_DIFF_PERCENTAGE:
          print(url, diff_amount)
          self.VULN_LINKS.append({
            "type": "AUTHEN_VULN",
            "link": link["url"],
            "vuln_link": f"{method} {url}",
            "diff": diff_amount
          })

        os.remove(FILE)
        os.remove(f"testing_{FILE}")
      os.chdir(self.cwd)
        