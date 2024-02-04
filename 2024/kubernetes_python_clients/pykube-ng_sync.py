import pykube
import time
import helpers.settings as settings
from datetime import datetime
import helpers.kubeconfig as kubeconfig

def main() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource = settings.create_random_ns()['ns_resource']

    start = time.perf_counter()

    api = pykube.HTTPClient(pykube.KubeConfig.from_file())

    # read
    pykube.Namespace.objects(api)
    pykube.Service.objects(api)
    pykube.Node.objects(api)
    pykube.ServiceAccount.objects(api)

    # write
    pykube.Namespace(api, test_namespace_resource).create()
    pykube.Namespace(api, test_namespace_resource).delete()

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