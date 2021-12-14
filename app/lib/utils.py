import os
import sys
import bs4
import requests
from colorama import Back, Fore, Style
from .constants import UserCrawlType, AuthKeywords
from urllib.parse import urlparse, parse_qsl, unquote_plus

class Utils:
  @staticmethod
  def print_banner():
    print("  ___   ____ __        __ _     ____  ")
    print(" / _ \ / ___|\ \      / // \   / ___| ")
    print("| | | |\___ \ \ \ /\ / // _ \  \___ \ ")
    print("| |_| | ___) | \ V  V // ___ \  ___) |")
    print(" \___/ |____/   \_/\_//_/   \_\|____/   v1.0")
    print("\nOptimized Solutions for Web-App Scanners")
    print("________________________________________\n\n")

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
  def check_authlink(url) -> bool:
    keywords = AuthKeywords
    html_output_name = urlparse(url).scheme

    res = requests.get(url)
    html_doc = res.text

    with open(html_output_name, 'w') as f:
      f.write(str(res.text))
      f.close()

    a_file = open(html_output_name)
    lines = a_file.readlines()

    # check check line if source code contains word in keyword dictionary
    for line in lines:
      if [ele for ele in keywords if (ele in str(line))]:
        a_file.close()
        os.remove(html_output_name)
        return True

    os.remove(html_output_name)
    # Check type="submit" and type="password"
    soup = bs4.BeautifulSoup(html_doc, 'html.parser')

    eles = soup.select("form input[type=submit]")
    eles1 = soup.select("form input[type=password]")

    if (bool(eles) and bool(eles1)):
      return True

    return False

  @staticmethod
  def pager_input(lines, limit):
    print(
      Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
      ' The following links are likely to be the login link:\n'
    )

    len_first_page = limit if len(lines) >= limit else len(lines)

    for i, line in enumerate(lines[0:len_first_page]):
      print(f"  {i+1}. {line}")

    if len(lines) <= limit:
      c = input(
        '\n' + Back.RED + Fore.WHITE + ' ? ' + Style.RESET_ALL +\
        f'Select link to login (1-{i}) or 0 if you cannot find one: '
      )

      if c.isdigit() and int(c) == 0:
        return None
      elif c.isdigit() and int(c) >= 1 and int(c) <= i:
        return lines[int(c)-1]
    else:
      remaining_pages = lines[len_first_page:]
      remaining_pages.append('')
      for i, line in enumerate(remaining_pages):
        i = limit + i
        if i == len(lines) - 1:
          print(
            Back.BLACK +\
            Fore.WHITE +\
            'END OF LINKS' +\
            Style.RESET_ALL
          )
          c = input(
            Back.BLACK +\
            Fore.WHITE +\
            f'Output page line 1-{i}/{len(lines)-1} - Select link to login (1-{i}) / 0 or ENTER if you cannot find one:' +\
            Style.RESET_ALL +\
            ' '
          )
        else:
          c = input(
            Back.BLACK +\
            Fore.WHITE +\
            f'Output page line 1-{i}/{len(lines)-1} - Select link to login (1-{i}) / 0 if you cannot find one / ENTER to view more:' +\
            Style.RESET_ALL +\
            ' '
          )

        if c.isdigit() and int(c) == 0:
          return None
        elif c.isdigit() and int(c) >= 1 and int(c) <= i:
          return lines[int(c)-1]
        else:
          if i != len(lines) - 1:
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            print(f"  {i+1}. {line}")
          else:
            return None
  
  @staticmethod
  def is_url_valid(url):
    # check if url is valid
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

  @staticmethod
  def format_url(url):
      return f"{urlparse(url).scheme}://{urlparse(url).netloc}/{'/'.join(list(filter(None, urlparse(url).path.split('/'))))}"

  @staticmethod
  def format_urls(list_urls):
    formatted_url = set()

    for url in list_urls:
      u = f"{urlparse(url).scheme}://{urlparse(url).netloc}/{'/'.join(list(filter(None, urlparse(url).path.split('/'))))}"
      formatted_url.add(u)

    return formatted_url

  @staticmethod
  def yes_no_question(question):
    os.system("clear")
    answer = input(
      Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
      f' {question} (y/n): '
    ).strip()
    print("")
    while not (answer == "y" or answer == "yes" or
               answer == "n" or answer == "no"):
      print("Input (yes/y) or (no/n)")
      answer = input(
        Back.BLACK + Fore.WHITE + ' > ' + Style.RESET_ALL +\
        f' {question} (y/n): '
      ).strip()
    if answer[0] == "y":
      return True
    else:
      return False

  @staticmethod
  def prompt_login(authen_url, driver):
    success = False
    if not authen_url is None:
      # open authen_url to login
      driver.get(authen_url)
      
      while True:
        if Utils.yes_no_question('Please confirm if you have logged in'):
          success = True
          break
        else:
          driver.get(authen_url)

    return success

  @staticmethod
  def map_link_traffic(link, target_id, output_dir, user_type):
    parent_dir = f"../output/{target_id}/{user_type}"
    path = os.path.join(parent_dir, output_dir)

    os.makedirs(path, exist_ok=True)
    if len(os.listdir('./')) != 0:
      os.chdir("../")
      os.system(f"mv ./tmp/* ./output/{target_id}/{user_type}/{output_dir}")
      os.chdir("tmp")

    return f"./output/{target_id}/{user_type}/{output_dir}"