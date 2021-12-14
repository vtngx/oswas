import requests
import webbrowser
import subprocess

class BurpSuite:

  # start burpsuite
  def start_burp(self):
    command = "./burp/burp-rest-api.sh --headless.mode=false --config-file=./burp/project-config.json --user-config-file=./burp/user-config.json"
    burp_api = subprocess.Popen(command, shell=True)
    return burp_api.pid

  # generate report
  def gen_report(self):
    headers = {
      'accept': '*/*',
    }

    report_params = (
      ('reportType', 'HTML'),
    )

    #using api to gen report
    requests.get('http://localhost:8090/burp/report', headers=headers, params=report_params)

    #open report page
    webbrowser.open('http://localhost:8090/burp/report?reportType=HTML', new=2)


  def get_status_code(self):
    try:
        requests.get('http://localhost:8090/v2/api-docs')
        return 200
    except Exception:
        return 500