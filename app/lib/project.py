import os
import colorama
from .db import Database
from .utils import Utils
from dotenv import load_dotenv
from .dirsearch import Dirsearch
from urllib.parse import urlparse, urljoin
from .constants import TargetStatus, UserCrawlType
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from queue import Queue


class Project:

  def __init__(self, options):
    load_dotenv()
    colorama.init()
    self.options = options
    self.db = Database()
    self.internal_urls = set()
    self.external_urls = set()
    self.urls = Queue()
    self.blacklist = ['logout', 'Logout', 'log out', 'Log out', 'thoat', 'Thoat', 'dangxuat', 'Dangxuat', 'dang xuat',
                 'Dang xuat', 'logOut', 'LogOut', 'log Out', 'Log Out', 'dangXuat', 'DangXuat', 'dang Xuat',
                 'Dang Xuat']
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
    choice = input('> Do you have login page? (y/N)')

    if not choice:
      choice = 'n'
    
    if choice.lower() == 'y':
      auth_url = input('> Please enter login page:')

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
      ds = Dirsearch(url, parseUrl)
      ds._run()
      ds_links = ds.getURL()

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
        print("!! dirsearch did not find any links")
        if Utils.check_authlink(url):
          auth_url = url
    
    if auth_url:
      # update uth_url of Target
      self.db.updateTarget(self.Target, { 'auth_url': auth_url })

    return auth_url   # None || found login link

  # MODULE 2
  def is_valid(self, url):
    # check if url is valid
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

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
      if not self.is_valid(href):
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

  def format_url(self):
    formatted_url = set()
    for url in self.internal_urls:
      u = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{'/'.join(list(filter(None, urlparse(url).path.split('/'))))}"
      formatted_url.add(u)
    return formatted_url

  def crawl(self, url, driver):
    # crawl a web page and get all links
    links = self.get_all_website_links(url)
    while True:
      # Open new Tab
      # print(links.qsize())
      driver.execute_script('''window.open("");''')
      driver.switch_to.window(driver.window_handles[1])
      # Open the first link we found in new tab
      new_link = links.get()
      for word in self.blacklist:
        if word in new_link:
          continue
      # print(new_link)
      driver.get(new_link)
      # time.sleep(1)
      # link we crawl can be different when we open it on browser
      current_url_in_browser = driver.current_url
      if current_url_in_browser != new_link:
        if current_url_in_browser in self.format_url():
          driver.close()
          driver.switch_to.window(driver.window_handles[0])
          if links.empty():
            return
          continue
      else:
        links = self.get_all_website_links(current_url_in_browser)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        if links.empty():
          return
        continue

  def yes_no_question(self, question):
    answer = input(question + "(y/n): ").lower().strip()
    print("")
    while not (answer == "y" or answer == "yes" or
               answer == "n" or answer == "no"):
      print("Input (yes/y) or (no/n)")
      answer = input(question + "(y/n):").lower().strip()
    if answer[0] == "y":
      return True
    else:
      return False

  def module2(self, authen_url, driver):
    if authen_url is None:
      driver.get(self.start_url)
      self.crawl(self.start_url, driver)
    else:
      driver.get(authen_url)
      while True:
        question = 'Are your sure you have logged in?'
        if self.yes_no_question(question):
          driver.get(self.start_url)
          self.crawl(self.start_url)
        else:
          driver.get(self.authen_url)
          continue

    print("Total Internal links:", len(self.internal_urls))
    print("Total External links:", len(self.external_urls))
    print("Total URLs:", len(self.external_urls) + len(self.internal_urls))
    return self.internal_urls
