# PyBOINC - a very basic python BOINC bridge
[![Build Status](https://travis-ci.com/nielstron/pyboinc.svg?branch=master)](https://travis-ci.com/nielstron/pyboinc)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/pyboinc/badge.svg?branch=master)](https://coveralls.io/github/nielstron/pyboinc?branch=master)
[![Package Version](https://img.shields.io/pypi/v/pyboinc)](https://pypi.org/project/PySyncThru/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyboinc.svg)](https://pypi.org/project/PySyncThru/)

A very basic package to connect to a [BOINC](https://boinc.berkeley.edu/) client in a pythonic way
based on the [BOINC GUI RPC Protocol](https://boinc.berkeley.edu/trac/wiki/GuiRpcProtocol).

## Usage

```python
import asyncio

from pyboinc import init_rpc_client

IP_BOINC = '127.0.0.1'


async def main():
    rpc_client = await init_rpc_client(IP_BOINC, "examplePasswordHere")
    print(await rpc_client._authorize())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
