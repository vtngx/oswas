import os
import json
import shutil
import requests
from pathlib import PurePath
from difflib import SequenceMatcher
from colorama.ansi import Back, Fore, Style

class Scanner:
  def __init__(self) -> None:
    self.MIN_DIFF_PERCENTAGE = 70
    self.VULN_LINKS = []
    self.AUTH_HEADER = 'authorization'
    self.COOKIE_HEADER = 'cookie'
    self.CSRF_SIG = ["csrf-token", "csrf_token", "token"]

    self.cwd = f'{os.getcwd()}/'
    self.testing_path = f"{os.getcwd()}/testing"
    os.system(f"rm -f {self.testing_path}/*")


  def run(self, links_noauth, links_user1, links_user2, links_admin):
    print(Back.GREEN + Fore.BLACK + 'SCANNING FOR VULNERABILITIES...' + Style.RESET_ALL + "\n")

    # scan authen vuln (user)
    if isinstance(links_user1, list) and len(links_user1) > 0:
      # get diff of links_noauath & links_user1
      diff_noauth_user = self.get_diff(links_user1, links_noauth)
      self.scan_authen_vuln(diff_noauth_user)
    
    # scan authen vuln (admin)
    if isinstance(links_admin, list) and len(links_admin) > 0:
      # get links only logged in user can access
      diff_noauth_admin = self.get_diff(links_admin, links_noauth)
      self.scan_authen_vuln(diff_noauth_admin)

    # scan vertical IDOR (user 1 & admin)
    if isinstance(links_user1, list) and len(links_user1) > 0 and isinstance(links_admin, list) and len(links_admin) > 0:
      self.scan_vtc_idor(links_admin, links_user1)

    # scan horizontal IDOR (user 1 & user 2)
    if isinstance(links_user1, list) and len(links_user1) > 0 and isinstance(links_user2, list) and len(links_user2) > 0:
      self.scan_hrz_idor(links_user1, links_user2)
    
    res = [i for n, i in enumerate(self.VULN_LINKS) if i not in self.VULN_LINKS[n + 1:]]
    print(f"\nVulns: {len(res)}\n\n")
    return res


  def get_diff(self, list_links_1, list_links_2):
    return (list(link for link in list_links_1 if link["url"] not in list(link["url"] for link in list_links_2)))


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
              content_l = content.read().lower()
              if self.AUTH_HEADER in content_l or self.COOKIE_HEADER in content_l:
                shutil.copy(os.path.join(r, file), self.testing_path)
                AUTH_FILES.append({
                  "url": url,
                  "file": file
                })

      os.chdir(self.testing_path)

      for item in AUTH_FILES:
        URL, FILE = item.values()
        body_data = []

        # get original headers & data
        with open(FILE, "r") as f_origin:
          lines = f_origin.read().splitlines()

          if lines[0].split()[1].startswith('http'):
            url = lines[0].split()[1]
          else:
            url = URL + lines[0].split()[1]

          method = lines[0].split()[0]
          is_header = True

          for line in lines[1:]:
            while is_header:
              if line == "\n" or line == "":
                is_header = False
                break
              x = line.split(':', 1)
              origin_header[x[0].strip()] = x[1].strip()
              break
            else:
              body_data.append(line)
        
        # map request body
        # try map to JSON format
        json_data = {}
        params = {}
        if len(body_data) > 0:
          if str(body_data[0]).startswith("{") and str(body_data[len(body_data)-1]).endswith("}"):
            with open(f'request_{FILE}', 'w') as f_req:
              for data in body_data:
                f_req.write(f'{data}\n')
            with open(f'request_{FILE}', 'r') as f_req_r:
              json_data = json.load(f_req_r)
          else:
            for param in body_data:
              p = param.split('&')
            if len(p) > 0:
              for value in p:
                v = value.split('=')
                if len(v) > 0:
                  params[v[0].strip()] = v[1].strip()

        # create testing request - remove auth headers
        with open(f"testing_{FILE}", "w") as f_noauth:
          tmp = None
          for line in lines:
            line_l = line.lower()
            if line_l.startswith(self.AUTH_HEADER) or line_l.startswith(self.COOKIE_HEADER):
              tmp = line
            if line != tmp:
              f_noauth.write('{}\n'.format(line))

        # get testing headers & data
        with open(f"testing_{FILE}", "r") as f_noauth_r:
          lines_noauth = f_noauth_r.read().splitlines()

          for line in lines_noauth[1:len(lines_noauth) - 1]:
            if line == "\n" or line == "":
              break
            x = line.split(':', 1)
            test_header[x[0].strip()] = x[1].strip()
        
        perform_test = False

        # send requests & get responses
        if method.lower() == 'get':
          perform_test = True
          res_o = requests.get(url, headers=origin_header)
          res_t = requests.get(url, headers=test_header)
        elif method.lower() in ['post', 'put']:
          res_o = requests.post(url, headers=origin_header, json=json_data, params=params)
          res_t = requests.get(url, headers=test_header, json=json_data, params=params)

        if perform_test:
          is_vuln = False
          # compare response text difference
          diff_amount = SequenceMatcher(None, res_o.text, res_t.text).ratio() * 100

          # add to vuln list if 2 responses are >= 70% similar 
          if res_t.status_code < 400:
            if diff_amount > self.MIN_DIFF_PERCENTAGE:
              is_vuln = True
              self.VULN_LINKS.append({
                "type": "Authentication Vulnerability",
                "link": link["url"],
                "vuln_link": f"{method} {url}",
                "diff": diff_amount
              })

          if is_vuln:
            print(Fore.RED + f'FOUND AUTH. VULN: {method.upper()} {url} {res_t.status_code} {"{:.2f}".format(diff_amount)}' + Style.RESET_ALL)
          else:
            print(f'TESTING AUTH. VULN: {method.upper()} {url} {res_t.status_code} {"{:.2f}".format(diff_amount)}')

        os.remove(FILE)
        os.remove(f"testing_{FILE}")
      os.chdir(self.cwd)


  def get_user_tokens(self, links):
    headers = []

    for link in links:
      if link["traffic_file"]:
        path = self.cwd + link["traffic_file"]

        # r=root, d=directories, f=files
        for r, d, f in os.walk(path):
          for file in f:
            if '.txt' in file:
              os.chdir(r)
              with open(file, "r") as content:
                content = content.read()
                content_l = content.lower()
                if self.AUTH_HEADER in content_l or self.COOKIE_HEADER in content_l:
                  lines = content.splitlines()
                  for line in lines:
                    line_l = line.lower()
                    if line_l.startswith(self.AUTH_HEADER) or line_l.startswith(self.COOKIE_HEADER):
                      x = line.split(':', 1)
                      headers.append({
                        "h": x[0].strip(),
                        "c": x[1].strip(),
                      })

    # remove duplicates and return list of headers
    return [i for n, i in enumerate(headers) if i not in headers[n + 1:]]


  def scan_idor(self, test_links, user_links, type):
    # get user auth/token headers
    user_auth_headers = self.get_user_tokens(user_links)

    # get files having auth headers
    for link in test_links:
      if link["traffic_file"]:
        TEST_FILES = []
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
                content = content.read()
                content_l = content.lower()

                # check if request has CSRF token
                has_csrf = False
                lines = content.splitlines()
                for line in lines:
                  line_l = line.lower()
                  if any(word in line_l for word in self.CSRF_SIG):
                    has_csrf = True
                
                if not has_csrf:
                  # check if request file has auth/cookie header
                  if self.AUTH_HEADER in content_l or self.COOKIE_HEADER in content_l:
                    shutil.copy(os.path.join(r, file), self.testing_path)
                    TEST_FILES.append({
                      "url": url,
                      "file": file
                    })

        os.chdir(self.testing_path)

        for item in TEST_FILES:
          URL, FILE = item.values()
          body_data = []

          # get original headers & data
          with open(FILE, "r") as f_origin:
            lines = f_origin.read().splitlines()

            if lines[0].split()[1].startswith('http'):
              url = lines[0].split()[1]
            else:
              url = URL + lines[0].split()[1]

            method = lines[0].split()[0]
            is_header = True

            for line in lines[1:]:
              while is_header:
                if line == "\n" or line == "":
                  is_header = False
                  break
                x = line.split(':', 1)
                origin_header[x[0].strip()] = x[1].strip()
                break
              else:
                body_data.append(line)
        
          # map request body
          # try map to JSON format
          json_data = {}
          params = {}
          if len(body_data) > 0:
            if str(body_data[0]).startswith("{") and str(body_data[len(body_data)-1]).endswith("}"):
              with open(f'request_{FILE}', 'w') as f_req:
                for data in body_data:
                  f_req.write(f'{data}\n')
              with open(f'request_{FILE}', 'r') as f_req_r:
                json_data = json.load(f_req_r)
            else:
              for param in body_data:
                p = param.split('&')
              if len(p) > 0:
                for value in p:
                  v = value.split('=')
                  if len(v) > 0:
                    params[v[0].strip()] = v[1].strip()

          for i, header in enumerate(user_auth_headers):
            test_file = f"testing_{i+1}_{FILE}"

            # create testing request files - add custom auth headers
            with open(test_file, "w") as f_test:
              for line in lines:
                line_l = line.lower()
                if line_l.startswith(self.AUTH_HEADER) or line_l.startswith(self.COOKIE_HEADER):
                  f_test.write(f'{header["h"]}: {header["c"]}\n')
                else:
                  f_test.write(f'{line}\n')

            # get testing headers & data
            with open(test_file, "r") as f_test_r:
              lines_test = f_test_r.read().splitlines()

              for line in lines_test[1:len(lines_test) - 1]:
                if line == "\n" or line == "":
                  break
                x = line.split(':', 1)
                test_header[x[0].strip()] = x[1].strip()
          
            perform_test = False

            # send requests & get responses
            if method.lower() == 'get':
              perform_test = True
              res_o = requests.get(url, headers=origin_header)
              res_t = requests.get(url, headers=test_header)
            elif method.lower() in ['post', 'put']:
              perform_test = True
              res_o = requests.post(url, headers=origin_header, json=json_data, params=params)
              res_t = requests.get(url, headers=test_header, json=json_data, params=params)

            if perform_test:
              is_vuln = False
              # compare response text difference
              diff_amount = SequenceMatcher(None, res_o.text, res_t.text).ratio() * 100

              # add to vuln list if 2 responses are >= 70% similar
              # & status code != 401 and 403
              if res_t.status_code < 400:
                if diff_amount > self.MIN_DIFF_PERCENTAGE:
                  is_vuln = True
                  self.VULN_LINKS.append({
                    "type": type,
                    "link": link["url"],
                    "vuln_link": f"{method} {url}",
                    "diff": diff_amount
                  })

              if is_vuln:
                print(Fore.RED + f'FOUND IDOR. VULN: {method.upper()} {url} {res_t.status_code} {"{:.2f}".format(diff_amount)}' + Style.RESET_ALL)
              else:
                print(f'TESTING IDOR. VULN: {method.upper()} {url} {res_t.status_code} {"{:.2f}".format(diff_amount)}')

            os.remove(test_file)
          os.remove(FILE)
        os.chdir(self.cwd)


  def scan_vtc_idor(self, links_admin, links_user):
    # get links only admin user can access
    diff_links = self.get_diff(links_admin, links_user)
    # scan vertical IDOR
    self.scan_idor(diff_links, links_user, "Vertical IDOR")


  def scan_hrz_idor(self, links_user1, links_user2):
    # test IDOR for user 1
    self.scan_idor(links_user1, links_user2, "Horizontal IDOR")
    # test IDOR for user 2
    self.scan_idor(links_user2, links_user1, "Horizontal IDOR")
