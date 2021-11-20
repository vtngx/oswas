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
    print(Back.GREEN + Fore.BLACK + 'SCANNING FOR VULNERABILITIES...' + Style.RESET_ALL)

    if isinstance(links_user1, list) and len(links_user1) > 0:
      # get diff of links_noauath & links_user1
      diff_noauth_user = (list(link for link in links_user1 if link["url"] not in list(link["url"] for link in links_noauth)))
      self.scan_authen_vuln(diff_noauth_user)
    
    if isinstance(links_admin, list) and len(links_admin) > 0:
      # get diff of links_noauath & links_admin
      diff_noauth_admin = (list(link for link in links_admin if link["url"] not in list(link["url"] for link in links_noauth)))
      self.scan_authen_vuln(diff_noauth_admin)

    # if isinstance(links_user1, list) and len(links_user1) > 0 and isinstance(links_admin, list) and len(links_admin) > 0:
    #   # get diff of links_user1 & links_admin
    #   diff_user1_admin = (list(link for link in links_admin if link["url"] not in list(link["url"] for link in links_user1)))
    #   self.scan_vtc_idor(diff_noauth_admin)
    
    print("Vulns:", len(self.VULN_LINKS))

  def scan_authen_vuln(self, links):
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

        # get original headers & data
        with open(FILE, "r") as f_origin:
          lines = f_origin.read().splitlines()

          method = lines[0].split()[0]
          url = URL + lines[0].split()[1]

          for line in lines[1:len(lines) - 1]:
            if line == "\n" or line == "":
              break
            x = line.split(':', 1)
            origin_header[x[0].strip()] = x[1].strip()

        # create testing request - remove auth headers
        with open(f"testing_{FILE}", "w") as f_noauth:
          tmp = None
          for line in lines:
            if line.startswith(self.AUTH_HEADER) or line.startswith(self.COOKIE_HEADER):
              tmp = line
            if line != tmp:
              f_noauth.write('{}\n'.format(line))

        # get testing headers & data
        with open(f"testing_{FILE}", "r") as f_noauth_r:
          lines_noauth = f_noauth_r.read().splitlines()

          method = lines_noauth[0].split()[0]
          url = URL + lines_noauth[0].split()[1]

          for line in lines_noauth[1:len(lines_noauth) - 1]:
            if line == "\n" or line == "":
              break
            x = line.split(':', 1)
            test_header[x[0].strip()] = x[1].strip()
        
        # send requests & get responses
        if method.lower() == 'get':
          res_o = requests.get(url, headers=origin_header)
          res_t = requests.get(url, headers=test_header)
        # elif method.lower() == 'post':
        #   res_o = requests.post(url, headers=origin_header)

        # compare respinse text difference
        diff_amount = SequenceMatcher(None, res_o.text, res_t.text).ratio() * 100

        print(f"{method.upper()} {url} {diff_amount}")

        # add to vuln list if 2 responses are likely similar
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
        
  # def scan_vtc_idor(self, links):
  #   for link in links:
  #     AUTH_FILES = []
  #     origin_header = {}
  #     test_header = {}
  #     method = ""

  #     origin_path = self.cwd + link["traffic_file"]

  #     # r=root, d=directories, f=files
  #     for r, d, f in os.walk(origin_path):
  #       for file in f:
  #         if '.txt' in file:
  #           url = PurePath(r).name.replace("\\\\", "://")
  #           os.chdir(r)
  #           with open(file) as content:
  #             if self.AUTH_HEADER in content.read() or self.COOKIE_HEADER in content.read():
  #               shutil.copy(os.path.join(r, file), self.testing_path)
  #               AUTH_FILES.append({
  #                 "url": url,
  #                 "file": file
  #               })

  #     os.chdir(self.testing_path)

  #     for item in AUTH_FILES:
  #       URL, FILE = item.values()

  #       # get original headers & data
  #       with open(FILE, "r") as f_origin:
  #         lines = f_origin.read().splitlines()

  #         method = lines[0].split()[0]
  #         url = URL + lines[0].split()[1]

  #         for line in lines[1:len(lines) - 1]:
  #           if line == "\n" or line == "":
  #             print(link)
  #             break
  #           x = line.split(':', 1)
  #           origin_header[x[0].strip()] = x[1].strip()

  #       # create testing request - remove auth headers
  #       with open(f"testing_{FILE}", "w") as f_noauth:
  #         tmp = None
  #         for line in lines:
  #           if line.startswith(self.AUTH_HEADER) or line.startswith(self.COOKIE_HEADER):
  #             tmp = line
  #           if line != tmp:
  #             f_noauth.write('{}\n'.format(line))

  #       # get testing headers & data
  #       with open(f"testing_{FILE}", "r") as f_noauth_r:
  #         lines_noauth = f_noauth_r.read().splitlines()

  #         method = lines_noauth[0].split()[0]
  #         url = URL + lines_noauth[0].split()[1]

  #         for line in lines_noauth[1:len(lines_noauth) - 1]:
  #           if line == "\n" or line == "":
  #             print(link)
  #             break
  #           x = line.split(':', 1)
  #           test_header[x[0].strip()] = x[1].strip()
        
  #       # send requests & get responses
  #       if method.lower() == 'get':
  #         res_o = requests.get(url, headers=origin_header)
  #         res_t = requests.get(url, headers=test_header)
  #       # elif method.lower() == 'post':
  #       #   res_o = requests.post(url, headers=origin_header)

  #       # compare respinse text difference
  #       diff_amount = SequenceMatcher(None, res_o.text, res_t.text).ratio() * 100

  #       print(f"{method.upper()} {url} {diff_amount}")

  #       # add to vuln list if 2 responses are likely similar
  #       if diff_amount > self.MIN_DIFF_PERCENTAGE:
  #         print(url, diff_amount)
  #         self.VULN_LINKS.append({
  #           "type": "AUTHEN_VULN",
  #           "link": link["url"],
  #           "vuln_link": f"{method} {url}",
  #           "diff": diff_amount
  #         })

  #       os.remove(FILE)
  #       os.remove(f"testing_{FILE}")
  #     os.chdir(self.cwd)