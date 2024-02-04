import time
import helpers.settings as settings
import asyncio
import helpers.kubeconfig as kubeconfig
from datetime import datetime
import kr8s.asyncio
from kr8s.asyncio.objects import Namespace

async def test() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource = settings.create_random_ns()['ns_resource']

    start = time.perf_counter()

    api = await kr8s.asyncio.api()
    #api = await kr8s.asyncio.api(kubeconfig='/home/gumbo/.kube/config.kr8s')

    test_namespace = Namespace(test_namespace_resource, api=api)

    # read
    await api.get("namespaces")
    await api.get("services")
    await api.get("nodes")
    await api.get("serviceaccounts")
    # write
    await test_namespace.create()
    await test_namespace.delete()

    end = time.perf_counter()

    now = datetime.now()
    hour = now.strftime("%H")

    return {'client': settings.Path(__file__).stem, 'endpoint': server, 'time': f'{end - start:.4f}', 'hour': hour }

async def main() -> None:
    for i in range(1, settings.ITERATIONS):
        data = await test()
        data['iteration'] = i
        data['round'] = settings.ROUND
        print(data)
        settings.to_csv(settings.FILE, 'a', data)

if __name__ == '__main__':
    asyncio.run(main())