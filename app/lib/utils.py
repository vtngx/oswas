import os
import bs4
import requests
from urllib.parse import urlparse, parse_qsl, unquote_plus

from .constants import LinkStatus, UserCrawlType

class Utils():
  # def __init__(self):

  @staticmethod
  def eq_urls(url1, url2):
    parts_1 = urlparse(url1)
    parts_2 = urlparse(url2)
    url1_parts = parts_1._replace(
      query=frozenset(parse_qsl(parts_1.query)),
      path=unquote_plus(parts_1.path)
    )
    url2_parts = parts_2._replace(
      query=frozenset(parse_qsl(parts_2.query)),
      path=unquote_plus(parts_2.path)
    )
    return url1_parts == url2_parts

  @staticmethod
  def linkToDbObject(url, auth=False, user=UserCrawlType.NO_AUTH, traffic_file=None, status=LinkStatus.TODO):
    return {
      "url": url,
      "auth": auth,
      "user": user,
      "traffic_file": None,
      "status": LinkStatus.TODO
    }

  @staticmethod
  def linksToDbObjectList(urls, auth=False, user=UserCrawlType.NO_AUTH, traffic_file=None, status=LinkStatus.TODO):
    list = []
    for url in urls:
      list.append({
        "url": url,
        "auth": auth,
        "user": user,
        "traffic_file": None,
        "status": LinkStatus.TODO
      })
    return list

  @staticmethod
  def check_authlink(url) -> bool:
    keywords = []
    html_output_name = urlparse(url).scheme

    # TODO: issues 
    # - ko check đc code của navbar/footer/...
    # - có ký tự ko encode được trên windows
    res = requests.get(url)
    html_doc = res.text

    with open(html_output_name, 'w') as f:
      f.write(res.text)
      f.close()

    a_file = open(html_output_name)
    lines = a_file.readlines()

    # check check line if source code contains word in keyword dictionary
    for line in lines:
      if [ele for ele in keywords if (ele in str(line))]:
        a_file.close()
        os.remove(html_output_name)
        return True

    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    # find_input_submit = soup.findAll(type="submit")
    # find_input_password = soup.findAll(type="password")
    find_form = soup.select('form')
    find_input_password = soup.select('form input[type="password"]')
    find_input_submit = soup.select('form input[type="submit"]')

    if bool(find_form and find_input_password and find_input_submit):
      return True

    return False