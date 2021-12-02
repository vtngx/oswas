import requests
import webbrowser
import subprocess


class BurpSuite:

  # start burpsuite
  def start_burp(self):
    command = "./burp/burp-rest-api.sh --headless.mode=false --config-file=./burp/project-config.json --user-config-file=./burp/user-config.json"
    burpApi = subprocess.Popen(command, shell=True)
    return burpApi.pid

  # generate report
  def gen_report(self):
    headers = {
      'accept': '*/*',
    }

    report_params = (
      ('reportType', 'HTML'),
    )

    #using api to gen report
    report_api = requests.get('http://localhost:8090/burp/report', headers=headers, params=report_params)

    #open report page
    webbrowser.open('http://localhost:8090/burp/report?reportType=HTML', new=2)
