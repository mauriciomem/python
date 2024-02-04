import time
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
import kr8s
from datetime import datetime
from kr8s.objects import Namespace

def main() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource = settings.create_random_ns()['ns_resource']

    start = time.perf_counter()

    api = kr8s.api()
    #api = kr8s.api(kubeconfig='/home/gumbo/.kube/config.kr8s')

    test_namespace = Namespace(test_namespace_resource, api=api)

    # read
    api.get("namespaces")
    api.get("services")
    api.get("nodes")
    api.get("serviceaccounts")
    # write
    test_namespace.create()
    test_namespace.delete()

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