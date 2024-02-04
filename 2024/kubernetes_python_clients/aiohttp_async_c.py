import aiohttp
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

async def get_core_resource(sess: aiohttp.ClientSession, server: str, name: str) -> Any:
    async with sess.get(f"{server}/api/v1/{name}") as response:
        return await response.json()

async def post_ns(sess: aiohttp.ClientSession, server: str, data: dict) -> Any:
    async with sess.post(f'{server}/api/v1/namespaces', data=data) as response:
        return await response.json()

async def delete_ns(sess: aiohttp.ClientSession, server: str, name: str) -> Any:
    async with sess.delete(f'{server}/api/v1/namespaces/{name}') as response:
        return await response.json()

async def test() -> dict:

    output = kubeconfig.load_kubeconfig()

    headers = {'Authorization': f'Bearer {output["token"]}'} if output['token'] else None
    server = output['server']
    ssl_context = kubeconfig.load_ssl(cacert=output['cacert'], cert=output['cert'], key=output['certkey'])

    test_namespace_resource, test_namespace_name = settings.create_random_ns().values()

    start = time.perf_counter()

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context),headers=headers) as sess:

        await run_parallel(
            get_core_resource(sess, server, 'namespaces'),
            get_core_resource(sess, server, 'services'),
            get_core_resource(sess, server, 'nodes'),
            get_core_resource(sess, server, 'serviceaccounts'),
            run_seq(
                post_ns(sess, server, test_namespace_resource),
                delete_ns(sess, server, test_namespace_name)
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