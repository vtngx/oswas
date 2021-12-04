import os
from .db import Database

class Report():
  def __init__(self) -> None:
    self.db = Database()
    self.targets = self.db.get_all_targets()
    if not os.path.isdir("../app/data/report-page/reports"):
      os.mkdir("../app/data/report-page/reports")
    if not os.path.isdir("../app/data/report-page/js/reports"):
      os.mkdir("../app/data/report-page/js/reports")


  def create_index_page(self):
    js_var = "var targets = [\n"
    for target in self.targets:
      _id = str(target["_id"])
      start_url = str(target["start_url"]).replace('"', '\\"').replace("'", "\\'").replace("\\", "/")
      status = str(target["status"])
      if "started_at" in target: started_at = str(target["started_at"])
      else: started_at = ""
      js_var += "    { _id: \""+_id+"\", start_url: \""+start_url+"\", started_at: \""+started_at+"\", status: \""+status+"\" },\n"
    js_var += "]\n"
    
    js = ""
    with open(f"../app/data/report-page/templates/init.js.txt", "r") as f:
      js = f.read()
    with open(f"../app/data/report-page/js/init.js", "w") as f:
      f.writelines(js_var)
      f.writelines(js)


  def create_report_files(self):
    for target in self.targets:
      _id = str(target["_id"])
      if os.path.isdir(f"output/{_id}"):
        vulns = target["vulns"]
        links_count = self.db.count_target_links(target["_id"])
        start_url = str(target["start_url"]).replace('"', '\\"').replace("'", "\\'").replace("\\", "/")
        status = str(target["status"])
        if "started_at" in target: started_at = str(target["started_at"])
        else: started_at = ""
        if "profiles" in target: profiles = str(target["profiles"])
        else: profiles = "0"

        with open(f"../app/data/report-page/js/reports/init_{_id}.js", "w") as f:
          js = f'document.getElementById("target-url").innerHTML = \"{start_url}\";\ndocument.getElementById("target-date").innerHTML = \"{started_at}\";\ndocument.getElementById("target-profiles").innerHTML = \"{profiles}\";\ndocument.getElementById("target-links").innerHTML = \"{links_count}\";\ndocument.getElementById("target-status").innerHTML = \"{status}\";\n\n'
          
          # write list vulns
          if len(vulns) > 0:
            js += 'const vulns = [\n'
            for vuln in vulns:
              link = str(vuln["link"]).replace('"', '\\"').replace("'", "\\'").replace("\\", "/")
              vuln_link = str(vuln["vuln_link"]).replace('"', '\\"').replace("'", "\\'").replace("\\", "/")
              js +=  '{ type: \"' + str(vuln["type"]) + '\", link: \"' + link + '\", vuln_link: \"' + vuln_link + '\" },\n'
            js += ']\n\n'
            with open(f"../app/data/report-page/templates/init_report.js.txt", "r") as ft:
              js += ft.read()
          else:
            js += 'document.getElementById("vulns").innerHTML = "<div class=\\"row\\">\\n<div class=\\"col\\">\\n<div class=\\"card border-left-dark shadow pt-4 pb-3 pl-4\\">\\n<h5>No IDOR/Authentication Vulnerabilites Found</h5>\\n</div>\\n</div>\\n</div>\\n"\n\n'

          # write sitemap
          if os.path.exists(os.path.join(os.getcwd(), f'output/{_id}/init_sitemap')):
            with open(f"output/{_id}/init_sitemap", "r") as fsm:
              js += fsm.read()

          f.writelines(js)

        html = ""
        with open(f"../app/data/report-page/templates/report.html.txt", "r") as f:
          html = f.read()
        with open(f"../app/data/report-page/reports/report_{_id}.html", "w") as f:
          f.writelines(html)
          f.writelines(f"<script src=\"../js/reports/init_{_id}.js\"></script>\n</body>\n</html>\n")


  def start_ui(self):
    os.chdir("../app/data/report-page")
    # if os.path.isdir("./node_modules"):
    #   os.system("rm -r node_modules")
    # os.system("npm install -s")
    os.system("npm start")