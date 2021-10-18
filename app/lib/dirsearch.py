import os
import os.path
from os import path

class Dirsearch:
  
  def __init__(self, url, parseUrl):
    self._install()
    self.url = url
    self.parseUrl = parseUrl
    self.output_file = str(self.parseUrl) + '.dsout.txt'

  # clone from gh & install
  def _install(self):
    if not path.exists('dirsearch'):
      os.system('git clone https://github.com/maurosoria/dirsearch.git')
      os.chdir('dirsearch')
      os.system('pip3 install -r requirements.txt')
      os.chdir("../")
    return 1

  # run dirsearch
  def _run(self):
    path = os.getcwd()
    os.chdir('dirsearch')
    os.system
    os.system(f'python3 dirsearch.py -q -u {self.url} -e php,js -i 200,300-399 -x 400-599 --format simple -o ../{self.output_file}')
    os.chdir("../")
    os.system('clear')

  # get links from dirsearch output
  def getURL(self):
    fileName = f'{self.output_file}'
    listUrl = []
    try:
      with open(fileName) as f:
        while (line := f.readline().rstrip()):
          listUrl.append(line)
      # delete dirsearch output file
      os.remove(fileName)
    except:
      pass
    return listUrl  