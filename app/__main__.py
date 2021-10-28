import sys
from selenium import webdriver
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

  # module 2

  driver1 = webdriver.Firefox()
  driver2 = webdriver.Firefox()
  driver3 = webdriver.Firefox()
  driver4 = webdriver.Firefox()

  if auth_url is None:
    project.module2(auth_url, driver1)
  else:
    project.module2("", driver1)
    project.module2(auth_url, driver2)

  while True:
    question = 'Do you have another user or admin account?'
    if project.yes_no_question(question):
      second_acc = input()
      admin_acc = input()
      project.module2(second_acc, driver3)
      project.module2(admin_acc, driver4)
      break
    else:
      break


if __name__ == "__main__":
  main()