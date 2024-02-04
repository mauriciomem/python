import asyncio
import time
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.api_client import ApiClient

async def test() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()
   
    start = time.perf_counter()

    await config.load_kube_config()

    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)
        # read
        await v1.list_namespace()
        await v1.list_namespaced_service(settings.NAMESPACE)
        await v1.list_node()
        await v1.list_namespaced_service_account(settings.NAMESPACE)
        # write
        await v1.create_namespace(test_namespace_resource)
        await v1.delete_namespace(test_namespace_name)
        
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