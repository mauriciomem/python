import helpers.settings as settings
import time
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from kubernetes import client, config

def main() -> None:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()

    start = time.perf_counter()

    config.load_kube_config()

    coreV1 = client.CoreV1Api()

    # read    
    coreV1.list_namespace()
    coreV1.list_namespaced_service(settings.NAMESPACE)
    coreV1.list_node()
    coreV1.list_namespaced_service_account(settings.NAMESPACE)
    # write
    coreV1.create_namespace(test_namespace_resource)
    coreV1.delete_namespace(test_namespace_name)

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