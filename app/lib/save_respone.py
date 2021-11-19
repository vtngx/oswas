import uuid

from mitmproxy.net.http.http1 import assemble_request

import os

from pathlib import Path

from urllib.parse import urlparse





# def insert(record):

#     # dump the details to JSON for later analysis

#     name = f'respone-{uuid.uuid4()}.json'

#     with open(directory / name, 'w') as f:

#         json.dump(record, f)



current_path = os.getcwd()





def request(flow):

    print('='*80)

    os.chdir(current_path)

    directory = Path(urlparse(flow.request.pretty_url).scheme + "\\\\" + urlparse(flow.request.pretty_url).netloc)

    directory.mkdir(exist_ok=True)

    os.chdir(f'./{directory}')

    print(os.getcwd())

    print('URL: '+flow.request.pretty_url)

    #create file .txt with random id

    name = f'request-{uuid.uuid4()}.txt'

    request_data = flow.request

    print('/n')

    print('*'*80)

    print(request_data)

    print('*'*80)

    #write decode request into file for later analysis

    with open(name, 'w') as f:

        f.write(assemble_request(request_data).decode('utf-8'))