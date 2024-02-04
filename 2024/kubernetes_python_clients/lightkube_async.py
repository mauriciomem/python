import time
import helpers.settings as settings
import asyncio
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from lightkube import AsyncClient 
from lightkube.resources.core_v1 import Namespace, Node, Service, ServiceAccount
from lightkube.models.meta_v1 import ObjectMeta

async def test() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_name = settings.create_random_ns()['ns_name']

    start = time.perf_counter()

    client = AsyncClient()

    test_namespace = Namespace(metadata=ObjectMeta(name=test_namespace_name))

    # read - list() returns an async iterable object
    client.list(Namespace)
    client.list(Service)
    client.list(Node)
    client.list(ServiceAccount)
    # write - create() and delete() returns asyncio Coroutines
    await client.create(test_namespace)
    await client.delete(Namespace, test_namespace_name)

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