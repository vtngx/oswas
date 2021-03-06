import os
import os.path
from urllib.parse import urlparse

class Dirsearch:
  
  def __init__(self, url, parse_url):
    self._install()
    self.url = url
    self.parse_url = parse_url
    self.output_file = str(self.parse_url) + '.dsout.txt'

  # clone from gh & install
  def _install(self):
    if not os.path.exists('dirsearch'):
      os.system('git clone https://github.com/maurosoria/dirsearch.git')
      os.chdir('dirsearch')
      os.system('pip3 install -r requirements.txt')
      os.chdir("../")
    return 1

  # run dirsearch
  def _run(self):
    os.chdir('dirsearch')
    os.system(f'python3 dirsearch.py -t 120 -u {self.url} -e php,js,asp,aspx,html -i 200-399 -x 400-599 --format simple -o ../{self.output_file}')
    os.chdir("../")
    os.system('clear')

  # get links from dirsearch output
  def get_url(self):
    file_name = f'{self.output_file}'
    list_urls = []
    
    try:
      with open(file_name) as f:
        while (line := f.readline().rstrip()):
          list_urls.append(line)
      # delete dirsearch output file
      os.remove(file_name)
    except Exception:
      pass
    
    if len(list_urls):
      url_shortened = [
        (f"{urlparse(url).scheme}://{urlparse(url).netloc}/{'/'.join(list(filter(None, urlparse(url).path.split('/')[1:3])))}")
        for url in list_urls
      ]
      list_urls = list(set(url_shortened))
      list_urls.sort()

    return list_urls