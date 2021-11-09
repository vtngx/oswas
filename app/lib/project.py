import os
import colorama
from queue import Queue
from .db import Database
from .utils import Utils
from dotenv import load_dotenv
from .dirsearch import Dirsearch
from .constants import BLACKLIST
from bson.objectid import ObjectId
from .form_spider import FormSpider
from .web_element import WebElementObj
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .constants import TargetStatus, UserCrawlType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class Project:

  def __init__(self, options):
    load_dotenv()
    colorama.init()
    self.options = options
    self.db = Database()
    self.Target = None
    self.auth_url = None
    self.MAX_TRIES = 1
    self.MAX_WAIT = 3


  # get arguments
  def get_args(self):
    return self.options


  # start function
  def start(self):
    os.system('clear')
    self.start_url = input('> Enter the URL: ')

    if (self.start_url):
      self.Target = self.db.createTarget({
        "start_url": self.start_url,
        "auth_url": None,
        "domain": urlparse(self.start_url).netloc,
        "status": TargetStatus.DOING,
      })


  # MODULE 1
  def find_auth_link(self):
    url = self.start_url
    auth_url = None

    # prompt user to input auth_link
    choice = input('?> Do you have login page? (y/N): ')

    if not choice:
      choice = 'n'
    
    if choice.lower() == 'y':
      auth_url = input('?> Please enter login page: ')
    elif choice.lower() == 'n':
      tmp = urlparse(url).netloc
      if tmp == '':
        parseUrl = url
      else:
        parseUrl = tmp

      # find links using dirsearch
      ds = Dirsearch(url, parseUrl)
      ds._run()
      ds_links = ds.getURL()

      if len(ds_links):
        # ask user to find login_url from list
        auth_url = Utils.pager_input(ds_links, 20)
      else:
        print("!> dirsearch did not find any links")

        # check if start_url is auth_url
        if Utils.check_authlink(url):
          auth_url = url
    
    # update auth_url of Target
    if auth_url:
      self.auth_url = auth_url
      self.db.updateTarget(self.Target, { 'auth_url': auth_url })

    return auth_url   # returns None or login link


  # MODULE 2
  def get_all_website_links(self, url, driver):
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    try:
      all_a_tags = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
      )
    except:
      all_a_tags = []

    for a_tag in all_a_tags:
      try:
        href = a_tag.get_attribute("href")
      except Exception as e:
      #   print(e)
        pass

      if not href:
        # href empty tag
        continue

      # join the URL if it's relative (not absolute link)
      href = urljoin(url, href)
      parsed_href = urlparse(href)

      # remove URL GET parameters, URL fragments, etc.
      href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
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
        select = element.element
        form_spider.fill_select(select)
      # fill inputs
      elif element.type == 'input':
        input = element.element
        form_spider.fill_input(input)
      # fill textareas
      elif element.type == 'textarea':
        textarea = element.element
        form_spider.fill_textarea(textarea)
      
    # find submit buttons/inputs
    submits = form_spider.find_elements_submit()

    # submit forms
    # open each form to new tabs
    for submit_element in submits:
      if submit_element.is_enabled() and submit_element.is_displayed():
        try:
          ActionChains(driver)\
            .key_down(Keys.CONTROL)\
            .click(submit_element)\
            .key_up(Keys.CONTROL)\
            .perform()
        except:
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

  def crawl(self, url, driver, userType):
    # remove redundant files im /tmp
    os.system("rm -rf *")
    os.mkdir(f"../output/{self.Target}")

    # crawl a web page and get all links
    links = self.get_all_website_links(url, driver)

    while True:
      # Open the first link we found in new tab
      # new_link la ten folder dang crawl
      new_link = links.get()
      print(f"CRAWL | {new_link}")

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
        traffic_path = Utils.map_link_traffic(new_link, str( self.Target), str(new_link_id))
        self.db_links.append({
          "_id": new_link_id,
          "url": new_link,
          "user": userType,
          "traffic_file": traffic_path,
        })

        if len(self.db_links) == 100:
          self.db.createLinksMulti(self.db_links)
          self.db_links = []
        
        driver.switch_to.window(driver.window_handles[0])
        print(f"DONE | {new_link}")
        self.done_links.append(new_link)
      except Exception as e:
        # print(e)
        print(f"FAIL | {new_link}")

      if links.empty():
        self.db.createLinksMulti(self.db_links)
        self.db.updateTarget(self.Target, { 'status': TargetStatus.DONE })
        return


  def start_crawler(self, driver, userType: UserCrawlType):
    self.internal_urls = set()
    self.external_urls = set()
    self.urls = Queue()
    self.done_links = []
    self.db_links = []

    if self.auth_url and not Utils.eq_urls(self.auth_url, self.start_url):
      self.db_links.append({
        "_id": ObjectId(),
        "url": self.auth_url,
        "user": userType,
        "traffic_file": None,
      })

    driver.get(self.start_url)
    self.crawl(self.start_url, driver, userType)
    driver.close()

    return self.done_links
