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
  project.find_auth_link()
  
if __name__ == "__main__":
  main()