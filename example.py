import asyncio

from pyboinc import init_rpc_client

IP_BOINC = "127.0.0.1"
PASSWORD_BOINC = "example_password"


async def main():
    rpc_client = await init_rpc_client(IP_BOINC, PASSWORD_BOINC)

    # Get status of current and older tasks
    print(await rpc_client.get_results())
    print(await rpc_client.get_project_status())
    print(await rpc_client.get_old_results())

    # Get last three messages
    c = await rpc_client.get_message_count()
    print(c)
    print(await rpc_client.get_messages(c-3))

    print(await rpc_client.get_notices_public(2))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
