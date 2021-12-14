import os
import colorama
import datetime
from queue import Queue
from .db import Database
from .utils import Utils
from .sitemap import Sitemap
from dotenv import load_dotenv
from .dirsearch import Dirsearch
from .constants import BLACKLIST
from bson.objectid import ObjectId
from .form_spider import FormSpider
from .web_element import WebElementObj
from urllib.parse import urlparse, urljoin
from colorama.ansi import Back, Fore, Style
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .constants import TargetStatus, UserCrawlType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class Project:

  def __init__(self):
    load_dotenv()
    colorama.init()
    self.db = Database()
    self.TARGET = None
    self.auth_url = None
    self.MAX_TRIES = 1
    self.MAX_WAIT = 2.5


  # start function
  def start(self):
    while True:
      self.start_url = input(
        Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
        ' Enter Web URL to start: '
      )

      if self.start_url:
        if not self.start_url.endswith("/"):
          self.start_url += "/"
        self.TARGET = self.db.create_target({
          "start_url": self.start_url,
          "auth_url": None,
          "domain": urlparse(self.start_url).netloc,
          "status": TargetStatus.DOING,
          "started_at": str(datetime.datetime.utcnow()),
          "profiles": 0,
          "vulns": []
        })
        os.makedirs(f"output/{self.TARGET}", exist_ok=True)
        break
      else:
        print(Fore.RED + 'PLEASE INPUT VALID URL' + Style.RESET_ALL)


  # MODULE 1
  def find_auth_link(self):
    url = self.start_url
    auth_url = None

    # prompt user to input auth_link
    choice = input(
      Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
      ' Do you have URL of this Website\'s login page? (y/N): '
    )

    if not choice:
      choice = 'n'
    
    if choice.lower() == 'y':
      auth_url = input(
        Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
        ' Please enter URL of login page: '
      )
    elif choice.lower() == 'n':
      tmp = urlparse(url).netloc
      if tmp == '':
        parse_url = url
      else:
        parse_url = tmp

      # find links using dirsearch
      ds = Dirsearch(url, parse_url)
      ds._run()
      ds_links = ds.get_url()

      if len(ds_links):
        # ask user to find login_url from list
        auth_url = Utils.pager_input(ds_links, 20)
      else:
        print(
          Back.RED + Fore.BLACK + ' !!! ' + Style.RESET_ALL +\
          " 0 LINKS FOUND FROM DIRSEARCH"
        )

        # check if start_url is auth_url
        if Utils.check_authlink(url):
          auth_url = url
    
    # update auth_url of Target
    if auth_url:
      self.auth_url = auth_url
      self.db.update_target(self.TARGET, { 'auth_url': auth_url })

    return auth_url   # returns None or login link


  # MODULE 2
  def get_all_website_links(self, url, driver):
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    try:
      all_a_tags = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
      )
    except Exception:
      all_a_tags = []

    for a_tag in all_a_tags:
      try:
        href = a_tag.get_attribute("href")
      except Exception:
        pass

      if not href:
        # href empty tag
        continue

      # join the URL if it's relative (not absolute link)
      href = urljoin(url, href)
      parsed_href = urlparse(href)

      # remove URL GET parameters, URL fragments, etc.
      href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
      
      if parsed_href.query:
        href = href + "?" + parsed_href.query

      if "pdf" in urlparse(href).path:
        self.internal_urls.add(href)
        continue

      if not Utils.is_url_valid(href):
        # not a valid URL
        continue

      if href in self.internal_urls:
        # already in the set
        continue

      # sua loi khi ten mien bi day ra khoi netloc(khac netloc)
      if domain_name != urlparse(href).netloc:
        # external link
        if href not in self.external_urls:
          self.external_urls.add(href)
        continue
      
      self.urls.put(href)
      self.internal_urls.add(href)
    return self.urls


  def crawl_from_forms(self, driver):
    try:
      form_spider = FormSpider(self.MAX_TRIES, self.MAX_WAIT, driver)
      selects = []
      inputs = []
      textareas = []

      # find inputs/textareas/selects
      selects = form_spider.find_elements_select()
      inputs = form_spider.find_elements_input()
      textareas = form_spider.find_elements_textarea()

      elements_to_fill = \
        list(map(WebElementObj.web_ele_2_select, selects)) + \
        list(map(WebElementObj.web_ele_2_input, inputs)) + \
        list(map(WebElementObj.web_ele_2_textarea, textareas))
      
      for element in elements_to_fill:
        # fill select boxes
        if element.type == 'select':
          form_spider.fill_select(element.element)
        # fill inputs
        elif element.type == 'input':
          form_spider.fill_input(element.element)
        # fill textareas
        elif element.type == 'textarea':
          form_spider.fill_textarea(element.element)
        
      # find submit buttons/inputs
      submits = form_spider.find_elements_submit()

      # submit forms
      # open each form to new tabs
      for submit_element in submits:
        if submit_element.is_enabled() and submit_element.is_displayed():
          try:
            # ActionChains(driver)\
            #   .key_down(Keys.CONTROL)\
            #   .click(submit_element)\
            #   .pause(5)\
            #   .key_up(Keys.CONTROL)\
            #   .perform()
            ActionChains(driver)\
              .click(submit_element)\
              .pause(5)\
              .perform()
          except Exception:
            pass
      
      # get number of open tabs
      open_tabs = driver.window_handles

      # only run when at least 1 new tab is opened
      if len(open_tabs) > 2:
        for i in range(len(open_tabs)-1, 1, -1):
          driver.switch_to.window(driver.window_handles[i])
          self.urls.put(driver.current_url)
          self.internal_urls.add(driver.current_url)
          driver.close()
        driver.switch_to.window(driver.window_handles[1])
    except Exception:
      pass


  def crawl(self, url, driver, user_type):
    # remove redundant files im /tmp
    os.system("rm -rf *")
    os.mkdir(f"../output/{self.TARGET}/{user_type}")

    # crawl a web page and get all links
    links = self.get_all_website_links(url, driver)

    while True:
      # Open the first link we found in new tab
      new_link = links.get()
      print(
        Back.YELLOW + Fore.BLACK + 'CRAWL' + Style.RESET_ALL +\
        f" {new_link}"
      )

      blacked = False
      for word in BLACKLIST:
        if word in new_link:
          blacked = True
      if blacked: continue

      try:
        # Open new Tab
        driver.execute_script('''window.open("");''')
        driver.switch_to.window(driver.window_handles[1])
      
        driver.get(new_link)
        driver.implicitly_wait(3)
        self.crawl_from_forms(driver)

        # redirected link handler
        current_url_in_browser = driver.current_url
        if current_url_in_browser != new_link:
          if current_url_in_browser not in Utils.format_urls(self.internal_urls):
            links.put(current_url_in_browser)
        else:
          links = self.get_all_website_links(current_url_in_browser, driver)

        driver.close()

        # mapping link - traffic files
        new_link_id = ObjectId()
        traffic_path = Utils.map_link_traffic(new_link, str( self.TARGET), str(new_link_id), user_type)
        self.db_links.append({
          "_id": new_link_id,
          "target_id": self.TARGET,
          "url": new_link,
          "user": user_type,
          "traffic_file": traffic_path,
        })

        if len(self.db_links) == 100:
          self.db.create_links_multi(self.db_links)
          self.db_links = []
        
        driver.switch_to.window(driver.window_handles[0])
        print(
          Back.GREEN + Fore.BLACK + 'DONE' + Style.RESET_ALL +\
          f" {new_link}"
        )
        self.done_links.append(new_link)
      except Exception:
        print(
          Back.RED + Fore.BLACK + 'FAIL' + Style.RESET_ALL +\
          f" {new_link}"
        )

      if links.empty():
        self.db.create_links_multi(self.db_links)
        self.db.update_target(self.TARGET, { 'status': TargetStatus.DONE })
        return


  def start_crawler(self, auth_url, driver, user_type: UserCrawlType):
    os.system("clear")
    print(
    Back.GREEN + Fore.BLACK + 'START CRAWLER' + Style.RESET_ALL +\
      f" {self.start_url} | " +\
      Back.LIGHTMAGENTA_EX + Fore.BLACK + 'PROFILE' + Style.RESET_ALL +\
      f" {user_type}\n"
    )

    self.internal_urls = set()
    self.external_urls = set()
    self.urls = Queue()
    self.done_links = []
    self.db_links = []

    if auth_url and not Utils.eq_urls(auth_url, self.start_url):
      self.db_links.append({
        "_id": ObjectId(),
        "target_id": self.TARGET,
        "url": auth_url,
        "user": user_type,
        "traffic_file": None,
      })

    driver.get(self.start_url)
    self.crawl(self.start_url, driver, user_type)
    driver.close()

    crawled_links = self.db.get_output_links(self.TARGET, user_type)

    return crawled_links


  def print_output_count(self, r_noauth, r_user1, r_user2, r_admin):
    os.system("clear")

    profiles_count = 0
    if r_noauth or isinstance(r_noauth, list): profiles_count += 1
    if r_user1  or isinstance(r_user1, list):  profiles_count += 1
    if r_user2  or isinstance(r_user2, list):  profiles_count += 1
    if r_admin  or isinstance(r_admin, list):  profiles_count += 1

    print(
      Back.GREEN + Fore.BLACK + 'CRAWL DONE' + Style.RESET_ALL +\
      f" {self.start_url} | " +\
      Back.LIGHTMAGENTA_EX + Fore.BLACK +\
      f" {profiles_count} PROFILES " +\
      Style.RESET_ALL + "\n"
    )
    if r_noauth or isinstance(r_noauth, list): print('NOAUTH:', len(r_noauth))
    if r_user1  or isinstance(r_user1, list):  print('USER 1:', len(r_user1))
    if r_user2  or isinstance(r_user2, list):  print('USER 2:', len(r_user2))
    if r_admin  or isinstance(r_admin, list):  print('ADMIN:' , len(r_admin))
    print()

  
  def create_sitemap(self):
    os.chdir(f"output/{self.TARGET}")
    links = self.db.get_all_target_links(self.TARGET)
    sm = Sitemap(self.start_url, links)
    sm.build_xml()
    sm.build_visual()
    os.chdir("../..")


  def update_target_profiles(self, profiles):
    self.db.update_target(self.TARGET, { 'profiles': profiles })


  def add_vulns_to_target(self, vulns):
    self.db.update_target(self.TARGET, { 'vulns': vulns })