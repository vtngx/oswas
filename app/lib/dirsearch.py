import os
import os.path
from os import path

class Dirsearch:
  
  def __init__(self, url, parseUrl):
    self._install()
    self.url = url
    self.parseUrl = parseUrl

  # clone from gh & install
  def _install(self):
    if not path.exists('dirsearch'):
      os.system('git clone https://github.com/maurosoria/dirsearch.git')
      os.chdir('dirsearch')
      os.system('pip3 install -r requirements.txt')
      os.chdir("../")
    print('dirsearch done')
    return 1

  # run dirsearch
  def _run(self):
    path = os.getcwd()
    print(path)
    os.chdir('dirsearch')
    os.system
    os.system(f'python3 dirsearch.py -u {self.url} -e php,js -x 403,401 --format simple -o ../{self.parseUrl}_report.txt')
    os.chdir("../")
    print('run dirsearch done')

  # get links from dirsearch output
  def getURL(self):
    fileName = f'{self.parseUrl}_report.txt'
    listUrl = []
    with open(fileName) as f:
      while (line := f.readline().rstrip()):
        listUrl.append(line)
    return listUrl  