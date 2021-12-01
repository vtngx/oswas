import os
import subprocess
import requests
import webbrowser


class BurpSuite:
    #edit path cho giong voi may


    #start burpsuite (de file config cung thu muc voi file cac file burp)
    def startBurp(self):   
        command = "./burp/burp-rest-api.sh  --headless.mode=false --config-file=./burp/project-config.json --user-config-file=./burp/user-config.json"
        burpApi = subprocess.Popen(command, shell=True)
        return burpApi.pid
        
    def genReport(self):
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
    

