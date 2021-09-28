import sys
from dotenv import load_dotenv

from lib import Project, Options, Database

def main():
  # load .env
  load_dotenv()

  # parse arguments
  options = Options()
  (opts, args) = options.parse(sys.argv[1:])

  # start app
  project = Project(opts)
  # print(project.get_args())

  # connect DB
  db = Database()

  
if __name__ == "__main__":
  main()