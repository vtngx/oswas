import os
import sys
import subprocess
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

  # 
  # MODULE 1
  # 
  # find login link
  #   prompt user (input/find with dirsearch)
  #   identify login link by signatures
  # 
  auth_url = project.find_auth_link()

  # 
  # MODULE 2
  # 
  # crawl new links with user authen & author
  #   crawl using no auth
  #   crawl using normal users
  #   crawl using admin
  # 

  #set up proxy for firefox
  directory = Path('tmp')
  directory.mkdir(exist_ok=True)

  os.chdir(f'./{directory}')

  script_path = "/home/kali/Desktop/Capstone/oswas/app/lib/"
  # cmd = f'qterminal -e mitmdump -s {script_path}/save_respone.py --mode upstream:http://127.0.0.1:8888 --ssl-insecure'
  cmd = f'qterminal -e mitmdump -s {script_path}/save_respone.py --mode upstream:http://127.0.0.1:8888 --ssl-insecure'
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
  

  # crawl no authen
  if auth_url is None:
    res_noauth = project.start_crawler(
      webdriver.Firefox(capabilities=firefox_capabilities),
      UserCrawlType.NO_AUTH
    )
  else:
    driver_user_1 = webdriver.Firefox(capabilities=firefox_capabilities)
    if Utils.prompt_login(auth_url, driver_user_1):
      res_user_1 = project.start_crawler(
        driver_user_1,
        UserCrawlType.USER1
      )
      res_noauth = project.start_crawler(
        webdriver.Firefox(capabilities=firefox_capabilities),
        UserCrawlType.NO_AUTH
      )

      has_user_2 = Utils.yes_no_question('> Do you have another user account?')
      has_admin = Utils.yes_no_question('> Do you have an admin account?')

      # crawl with user 2
      if has_user_2:
        driver_user_2 = webdriver.Firefox(capabilities=firefox_capabilities)
        if Utils.prompt_login(auth_url, driver_user_2):
          res_user_2 = project.start_crawler(
            driver_user_2,
            UserCrawlType.USER2
          )

      # crawl with admin
      if has_admin:
        driver_admin = webdriver.Firefox(capabilities=firefox_capabilities)
        if Utils.prompt_login(auth_url, driver_admin):
          res_admin = project.start_crawler(
            driver_admin,
            UserCrawlType.ADMIN
          )


  # crawler results
  # if res_noauth: links_noauth = res_noauth
  # if res_user_1: links_user_1 = res_user_1
  # if res_user_2: links_user_2 = res_user_2
  # if res_admin: links_admin = res_admin

  # print('crawl noauth:', len(links_noauth) or 0)
  # print('crawl user 1:', len(links_user_1) or 0)
  # print('crawl user 2:', len(links_user_2) or 0)
  # print('crawl admin:' , len(links_admin) or 0)

  os.kill(int(mitmproxy.pid), 0)


if __name__ == "__main__":
  main()