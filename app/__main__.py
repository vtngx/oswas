import sys

from lib import Project, Options

def main():
  # parse arguments
  options = Options()
  (opts, args) = options.parse(sys.argv[1:])

  # start app
  project = Project(opts)
  project.start()

  # run module 1
  # find login link
  auth_url = project.find_auth_link()

  print(auth_url)

  # if auth_url is found (!= None)
  project.module2(auth_url)

  
if __name__ == "__main__":
  main()