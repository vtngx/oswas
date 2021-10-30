import sys
import threading
from lib.utils import Utils
from selenium import webdriver
from lib import Project, Options
from multiprocessing import Process
from multiprocessing.pool import ThreadPool
import subprocess
import os
from pathlib import Path


def main():
  # parse arguments
  options = Options()
  (opts, args) = options.parse(sys.argv[1:])

  # # crawler threads handler
  # threadLocal = threading.local()
  # threadLock = threading.Lock()

  # def get_driver(driver_name):
  #   driver = getattr(threadLocal, driver_name, None)
  #   if driver is None:
  #     driver = driver_user_1
  #     setattr(threadLocal, driver_name, driver)
  #   return driver

  # class CrawlerHandlerThread(threading.Thread):
  #   def __init__(self, driver_name):
  #     threading.Thread.__init__(self)
  #     self.driver_name = driver_name
  #     self._return = None
  #   def run(self):
  #     print('>> start user')
  #     threadLock.acquire()
  #     driver = get_driver(self.driver_name)
  #     links = project.start_crawler(driver)
  #     self._return = links
  #     threadLock.release()
  #   def join(self):
  #     threading.Thread.join(self)
  #     return self._return

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
  directory = Path('output')
  directory.mkdir(exist_ok=True)

  os.chdir(f'./{directory}')

  script_path = "/home/kali/Desktop/Capstone/oswas/app/lib"
  cmd = f'qterminal -e mitmdump -s {script_path}/save_respone.py'
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
    res_noauth = project.start_crawler(webdriver.Firefox(capabilities=firefox_capabilities))
  else:
    driver_user_1 = webdriver.Firefox()
    if project.prompt_login(auth_url, driver_user_1):
      res_user_1 = project.start_crawler(driver_user_1)
      res_noauth = project.start_crawler(webdriver.Firefox())

      has_user_2 = Utils.yes_no_question('> Do you have another user account?')
      has_admin = Utils.yes_no_question('> Do you have an admin account?')

      # crawl with user 2
      if has_user_2:
        driver_user_2 = webdriver.Firefox()
        if project.prompt_login(auth_url, driver_user_2):
          res_user_2 = project.start_crawler(driver_user_2)

      # crawl with admin
      if has_admin:
        driver_admin = webdriver.Firefox()
        if project.prompt_login(auth_url, driver_admin):
          res_admin = project.start_crawler(driver_admin)

  print('crawl noauth:', len(res_noauth['internal_urls']))
  print('crawl user 1:', len(res_user_1['internal_urls']))
  print('crawl user 2:', len(res_user_2['internal_urls']))
  print('crawl admin:' , len(res_admin['internal_urls']))
  os.kill(int(mitmproxy.pid), 0)


if __name__ == "__main__":
  main()



  # # crawl no authen
  # driver_noauth = webdriver.Firefox()
  # thread_noauth = CrawlerHandlerThread('driver_noauth')

  # if auth_url is None:
  #   thread_noauth.start()
  #   thread_noauth.join()
  # else:
  #   driver_user_1 = webdriver.Firefox()
  #   if project.prompt_login(auth_url, driver_user_1):
  #     thread_user_1 = CrawlerHandlerThread('driver_user_1')
  #     thread_noauth.start()
  #     thread_user_1.start()
  #     links_1 = thread_noauth.join()
  #     links_2 = thread_user_1.join()
  #     print('links noauth:', len(links_1))
  #     print('links user 1:', len(links_2))