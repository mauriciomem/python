import httpx
import asyncio
import time
import helpers.settings as settings
import helpers.kubeconfig as kubeconfig
from datetime import datetime
from typing import Any, Awaitable

async def run_parallel(*functions: Awaitable[Any]) -> None:
    await asyncio.gather(*functions)

async def run_seq(*functions: Awaitable[Any]) -> None:
    for func in functions:
        await func

async def get_core_resource(client: httpx.AsyncClient, server: str, name: str) -> Any:
    response = await client.get(f"{server}/api/v1/{name}")
    return response.json()

async def post_ns(client: httpx.AsyncClient, server: str, data: dict) -> Any:
    response = await client.post(f'{server}/api/v1/namespaces', json=data)
    return response.json()

async def delete_ns(client: httpx.AsyncClient, server: str, name: str) -> Any:
    response = await client.delete(f'{server}/api/v1/namespaces/{name}')
    return response.json()

async def test() -> dict:

    output = kubeconfig.load_kubeconfig()

    headers = {'Authorization': f'Bearer {output["token"]}'} if output['token'] else None
    server = output['server']
    cacert = output['cacert']
    cert = (output['cert'], output['certkey']) if output['cert'] and output['certkey'] else None

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()

    start = time.perf_counter()

    async with httpx.AsyncClient(verify=cacert, cert=cert, headers=headers) as client:

        await run_parallel(
            get_core_resource(client, server, 'namespaces'),
            get_core_resource(client, server, 'services'),
            get_core_resource(client, server, 'nodes'),
            get_core_resource(client, server, 'serviceaccounts'),
            run_seq(
                post_ns(client, server, test_namespace_resource),
                delete_ns(client, server, test_namespace_name)
            )
        )

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
