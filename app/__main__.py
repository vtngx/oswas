import os
import sys
import subprocess
from lib import Scanner
from pathlib import Path
from lib.utils import Utils
from selenium import webdriver
from lib import Project, Options
from lib.constants import UserCrawlType


def main():
  # parse arguments
  options = Options()
  (opts, args) = options.parse(sys.argv[1:])

  # start app
  project = Project(opts)
  project.start()

  # identify auth url
  auth_url = project.find_auth_link()

  #set up proxy for firefox
  directory = Path('tmp')
  directory.mkdir(exist_ok=True)
  script_p = f"{os.getcwd()}/../app/lib/save_respone.py"

  os.chdir(f'./{directory}')

  cmd = f'qterminal -e mitmdump -s {script_p} --ssl-insecure'
  # cmd = f'qterminal -e mitmdump -s {script_p} --mode upstream:http://127.0.0.1:8888 --ssl-insecure'
  mitmproxy = subprocess.Popen(cmd, shell=True)

  proxy = '127.0.0.1:8080'
  firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
  firefox_capabilities['marionette'] = True
  firefox_capabilities['proxy'] = {
        "proxyType": "MANUAL",
        "httpProxy": proxy,
        "sslProxy": proxy,
        "socksProxy": proxy,
        "socksVersion": 5
  }   
  firefox_capabilities['acceptInsecureCerts'] = True
  firefox_capabilities['acceptSslCerts'] = True

  res_noauth = None
  res_user_1 = None
  res_user_2 = None
  res_admin  = None

  # crawl no authen
  if auth_url is None:
    res_noauth = project.start_crawler(
      None,
      webdriver.Firefox(capabilities=firefox_capabilities),
      UserCrawlType.NO_AUTH
    )
  else:
    driver_user_1 = webdriver.Firefox(capabilities=firefox_capabilities)
    if Utils.prompt_login(auth_url, driver_user_1):
      res_user_1 = project.start_crawler(
        auth_url,
        driver_user_1,
        UserCrawlType.USER1
      )
      res_noauth = project.start_crawler(
        None,
        webdriver.Firefox(capabilities=firefox_capabilities),
        UserCrawlType.NO_AUTH
      )

      # crawl with user 2
      has_user_2 = Utils.yes_no_question('> Do you have another user account?')
      if has_user_2:
        driver_user_2 = webdriver.Firefox(capabilities=firefox_capabilities)
        if Utils.prompt_login(auth_url, driver_user_2):
          res_user_2 = project.start_crawler(
            auth_url,
            driver_user_2,
            UserCrawlType.USER2
          )

      # crawl with admin
      has_admin = Utils.yes_no_question('> Do you have an admin account?')
      if has_admin:
        driver_admin = webdriver.Firefox(capabilities=firefox_capabilities)
        if Utils.prompt_login(auth_url, driver_admin):
          res_admin = project.start_crawler(
            auth_url,
            driver_admin,
            UserCrawlType.ADMIN
          )

  os.kill(int(mitmproxy.pid), 0)
  os.chdir("..")

  # crawler results
  project.print_output_count(res_noauth, res_user_1, res_user_2, res_admin)

  # test for authen + IDOR vulnerabilities
  directory = Path('testing')
  directory.mkdir(exist_ok=True)
  Scanner().run(res_noauth, res_user_1, res_user_2, res_admin)



if __name__ == "__main__":
  main()