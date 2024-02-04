import asyncio
import pykube
import time
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from typing import Awaitable, Any

# own async implementation with a custom approach to execute the client request as performant as possible. No native support

async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

async def run_seq(*functions: Awaitable[Any]) -> None:
    for func in functions:
        await func

async def get_resource(api: pykube.HTTPClient, pykube_class: Any) -> Awaitable[Any]:
    return await loop.run_in_executor(None, pykube_class.objects, api)

async def create_resource(api: pykube.HTTPClient, resource: Any) -> Awaitable[Any]:
    return await loop.run_in_executor(None, resource.create)

async def delete_resource(api: pykube.HTTPClient, resource: Any) -> Awaitable[Any]:
    return await loop.run_in_executor(None, resource.delete)

async def main() -> dict:

    server = kubeconfig.load_kubeconfig()['server']

    test_namespace_resource = settings.create_random_ns()['ns_resource']

    start = time.perf_counter()

    kube_config = pykube.KubeConfig.from_file()
    api = pykube.HTTPClient(kube_config)

    await run_parallel(
        # read
        get_resource(api, pykube.Namespace),
        get_resource(api, pykube.Service),
        get_resource(api, pykube.Node),
        get_resource(api, pykube.ServiceAccount),
        # write
        run_seq(
            create_resource(api,pykube.Namespace(api, test_namespace_resource)),
            delete_resource(api,pykube.Namespace(api, test_namespace_resource))
        )
    )
   
    end = time.perf_counter()

    now = datetime.now()
    hour = now.strftime("%H")

    return {'client': settings.Path(__file__).stem, 'endpoint': server, 'time': f'{end - start:.4f}', 'hour': hour }

if __name__ == '__main__':
    for i in range(1, settings.ITERATIONS):
        loop = asyncio.new_event_loop()
        data = loop.run_until_complete(main())
        data['iteration'] = i
        data['round'] = settings.ROUND
        print(data)
        settings.to_csv(settings.FILE, 'a', data)