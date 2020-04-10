import asyncio

from pyboinc import init_rpc_client

IP_BOINC = '127.0.0.1'


async def main():
    rpc_client = await init_rpc_client(IP_BOINC, "examplePasswordHere")
    print(await rpc_client._authorize())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
