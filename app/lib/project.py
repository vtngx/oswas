import os
import colorama
import requests
from queue import Queue
from .db import Database
from .utils import Utils
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from .dirsearch import Dirsearch
from .constants import BLACKLIST
from .form_spider import FormSpider
from .web_element import WebElementObj
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.keys import Keys
from .constants import TargetStatus, UserCrawlType
from selenium.webdriver.common.action_chains import ActionChains


class Project:

  def __init__(self, options):
    load_dotenv()
    colorama.init()
    self.options = options
    self.db = Database()
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
        "domain": "",
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

      # add Links to DB
      if (Utils.eq_urls(url, auth_url)):
        link_db = Utils.linkToDbObject(url, True, UserCrawlType.USER1)
        self.db.createLink(link_db)
      else:
        links_db = [url, auth_url]
        self.db.createLinksMulti(Utils.linksToDbObjectList(links_db, True, UserCrawlType.USER1))
    elif choice.lower() == 'n':
      tmp = urlparse(url).netloc
      if tmp == '':
        parseUrl = url
      else:
        parseUrl = tmp

      # find links using dirsearch
      # ds = Dirsearch(url, parseUrl)
      # ds._run()
      # ds_links = ds.getURL()
      ds_links = []

      if len(ds_links):
        # ask user to find login_url from list
        auth_url = Utils.pager_input(ds_links, 20)
      
        if auth_url:
          ds_links.append(url)

          # add Links to DB
          links_db = Utils.linksToDbObjectList(ds_links, True, UserCrawlType.USER1)
        else:
          # add Links to DB
          links_db = Utils.linksToDbObjectList(ds_links)

          # check if start_url is auth_link
          if Utils.check_authlink(url):
            auth_url = url

        self.db.createLinksMulti(links_db)
      else:
        print("!> dirsearch did not find any links")
        if Utils.check_authlink(url):
          auth_url = url
    
    if auth_url:
      # update uth_url of Target
      self.db.updateTarget(self.Target, { 'auth_url': auth_url })

    return auth_url   # returns None or login link


  # MODULE 2
  def get_all_website_links(self, url):
    # all URLs of `url`
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    for a_tag in soup.findAll("a"):
      href = a_tag.attrs.get("href")

      if href == "" or href is None:
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

    print(f'> {len(selects)} selects')
    print(f'> {len(inputs)} inputs')
    print(f'> {len(textareas)} textareas')

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
        ActionChains(driver)\
          .key_down(Keys.CONTROL)\
          .click(submit_element)\
          .key_up(Keys.CONTROL)\
          .perform()
    
    # get number of open tabs
    open_tabs = driver.window_handles

    # only run when at least 1 new tab is opened
    if len(open_tabs) > 1:
      for i in range(len(open_tabs)-1, 1, -1):
        driver.switch_to.window(driver.window_handles[i])
        self.urls.put(driver.current_url)
        self.internal_urls.add(driver.current_url)
        driver.close()
      driver.switch_to.window(driver.window_handles[1])

  def crawl(self, url, driver):
    # crawl a web page and get all links
    links = self.get_all_website_links(url)
    while True:
      
      # Open new Tab
      driver.execute_script('''window.open("");''')
      driver.switch_to.window(driver.window_handles[1])

      # Open the first link we found in new tab
      new_link = links.get()

      for word in BLACKLIST:
        if word in new_link:
          continue
      
      driver.get(new_link)
      self.crawl_from_forms(driver)

      # redirected link handler
      current_url_in_browser = driver.current_url
      if current_url_in_browser != new_link:
        if current_url_in_browser not in Utils.format_urls(self.internal_urls):
          links.put(current_url_in_browser)
      else:
        links = self.get_all_website_links(current_url_in_browser)

      driver.close()
      driver.switch_to.window(driver.window_handles[0])
      if links.empty():
        return


  def prompt_login(self, authen_url, driver):
    success = False
    if not authen_url is None:
      # open authen_url to login
      driver.get(authen_url)
      
      while True:
        if Utils.yes_no_question('?> Please confirm if you have logged in '):
          success = True
          break
        else:
          driver.get(authen_url)

    return success


  def start_crawler(self, driver):
    self.internal_urls = set()
    self.external_urls = set()
    self.urls = Queue()

    driver.maximize_window()
    driver.get(self.start_url)
    self.crawl(self.start_url, driver)
    driver.close()
    
    # print("Total Internal links:", len(self.internal_urls))
    # print("Total External links:", len(self.external_urls))
    # print("Total URLs:", len(self.external_urls) + len(self.internal_urls))

    return dict({
      'internal_urls': self.internal_urls,
      'external_urls': self.external_urls,
    })
