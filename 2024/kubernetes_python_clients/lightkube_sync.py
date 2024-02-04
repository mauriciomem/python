import time
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from lightkube import Client
from lightkube.resources.core_v1 import Namespace, Node, Service, ServiceAccount
from lightkube.models.meta_v1 import ObjectMeta

def main() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_name = settings.create_random_ns()['ns_name']

    start = time.perf_counter()

    client = Client()

    test_namespace = Namespace(metadata=ObjectMeta(name=test_namespace_name))

    # read
    client.list(Namespace)
    client.list(Service)
    client.list(Node)
    client.list(ServiceAccount)
    # write
    client.create(test_namespace)
    client.delete(Namespace, name=test_namespace_name)

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