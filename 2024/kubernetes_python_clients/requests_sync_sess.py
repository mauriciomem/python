import requests
import time
import json
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from typing import Any

def get_core_resource(sess: requests.Session, server: str, name: str) -> Any:
    response = sess.get(f'{server}/api/v1/{name}')
    return response.json()

def post_ns(sess: requests.Session, server: str, data: dict) -> Any:
    response = sess.post(f'{server}/api/v1/namespaces', data=json.dumps(data))
    return response.json()

def delete_ns(sess: requests.Session, server: str, name: str) -> Any:
    response = sess.delete(f'{server}/api/v1/namespaces/{name}')
    return response.json()

def main() -> dict:

    output = kubeconfig.load_kubeconfig()

    headers = {'Authorization': f'Bearer {output["token"]}'} if output['token'] else None
    server = output['server']
    cacert = output['cacert']
    cert = (output['cert'], output['certkey']) if output['cert'] and output['certkey'] else None

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()

    start = time.perf_counter()

    with requests.Session() as sess:

        sess.cert = cert
        sess.verify = cacert
        if headers:
            sess.headers.update(headers)

        get_core_resource(sess, server, 'namespaces')
        get_core_resource(sess, server, 'services')
        get_core_resource(sess, server, 'nodes')
        get_core_resource(sess, server, 'serviceaccounts')
        post_ns(sess, server, test_namespace_resource)
        delete_ns(sess, server, test_namespace_name)

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