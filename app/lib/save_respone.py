import os
import uuid
from pathlib import Path
from urllib.parse import urlparse
from mitmproxy.net.http.http1 import assemble_request

current_path = os.getcwd()

def request(flow):
    os.chdir(current_path)
    directory = Path(urlparse(flow.request.pretty_url).scheme + "\\\\" + urlparse(flow.request.pretty_url).netloc)
    directory.mkdir(exist_ok=True)
    os.chdir(f'./{directory}')

    #create file .txt with random id
    name = f'request-{uuid.uuid4()}.txt'
    request_data = flow.request

    #write decode request into file for later analysis
    with open(name, 'w') as f:
        try:
            f.write(assemble_request(request_data).decode('utf-8'))
        except Exception:
            print('Decode UTF-8 faild.')