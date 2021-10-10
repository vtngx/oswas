from .db import Database
from .utils import Utils
from dotenv import load_dotenv
from .dirsearch import Dirsearch
from urllib.parse import urlparse
from .constants import TargetStatus, UserCrawlType

class Project:

  def __init__(self, options):
    load_dotenv()
    self.options = options
    self.db = Database()

  # get arguments
  def get_args(self):
    return self.options

  # start function
  def start(self):
    print('> Enter the URL: ')
    self.start_url = input()

    if (self.start_url):
      self.db.createTarget({
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
    print("> Do you have login page ?(y/n)")
    choice = input()
    
    if choice.lower() == 'y':
      print("> Please enter login page:")
      auth_url = input()

      # TODO: manual login with Selenium

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

      # ask user to find login_url from list
      print("> The following links are likely to be the login link")
      for link in ds_links:
        print("-", link)

      print(f"\n> Please select link to login (1-{len(ds_links)}) or select 0 if you cannot find one:")
      choice = int(input())
      if choice != 0:
        auth_url = ds_links[(choice)]
        ds_links.append(url)

        # TODO: manual login with Selenium

        # add Links to DB
        links_db = Utils.linksToDbObjectList(ds_links, True, UserCrawlType.USER1)
      else:
        # add Links to DB
        links_db = Utils.linksToDbObjectList(ds_links)

        # check if start_url is auth_link
        if Utils.check_authlink(url):
          auth_url = url
          # TODO: manual login with Selenium
          print('manual login')

      self.db.createLinksMulti(links_db)
    
    if auth_url:
      # update Target
      print()

    return auth_url   # None || found login link