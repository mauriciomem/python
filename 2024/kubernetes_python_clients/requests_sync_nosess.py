import requests
import time
import json
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from typing import Any

def get_core_resource(server: str, name: str, ca: str, cert: tuple, headers: dict) -> Any:
    response = requests.get(f'{server}/api/v1/{name}', verify=ca, cert=cert, headers=headers)
    return response.json()

def post_ns(server: str, data: dict, ca: str, cert: tuple, headers: dict) -> Any:
    response = requests.post(f'{server}/api/v1/namespaces', verify=ca, cert=cert, data=json.dumps(data), headers=headers)
    return response.json()

def delete_ns(server: str, name: str, ca: str, cert: tuple, headers: dict) -> Any:
    response = requests.delete(f'{server}/api/v1/namespaces/{name}', verify=ca, cert=cert, headers=headers)
    return response.json()

def main() -> dict:

    output = kubeconfig.load_kubeconfig()

    headers = {'Authorization': f'Bearer {output["token"]}'} if output['token'] else None
    server = output['server']
    cacert = output['cacert']
    cert = (output['cert'], output['certkey']) if output['cert'] and output['certkey'] else None

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()

    start = time.perf_counter()

    get_core_resource(server, 'namespaces', cacert, cert, headers)
    get_core_resource(server, 'services', cacert, cert, headers)
    get_core_resource(server, 'nodes', cacert, cert, headers)
    get_core_resource(server, 'serviceaccounts', cacert, cert, headers)
    post_ns(server, test_namespace_resource, cacert, cert, headers)
    delete_ns(server, test_namespace_name, cacert, cert, headers)

    end = time.perf_counter()
    
    now = datetime.now()
    hour = now.strftime("%H")

    return {'client': settings.Path(__file__).stem, 'endpoint': server, 'time': f'{end - start:.4f}', 'hour': hour }

if __name__ == '__main__':
    for i in range(1, settings.ITERATIONS):
        data = main()
        data['iteration'] = i
        data['round'] = settings.ROUND
        print(data)
        settings.to_csv(settings.FILE, 'a', data)