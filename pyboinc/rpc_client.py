"""
Client making requests to RPC server
managing authentication etc
"""

from .raw_client import _RPCClientRaw
import xml.etree.ElementTree as ET
from hashlib import md5

class TAG:

    AUTH1 = "auth1"
    NONCE = "nonce"
    AUTH2 = "auth2"
    NONCE_HASH = "nonce_hash"
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"


async def init_rpc_client(host: str, password=None):
    """
    Creates RPC Client and initiates connection to RPC Server
    """
    c = RPCClient(host, password)
    await c.connect()
    return c

class RPCClient:

    def __init__(self, host: str, password=None):
        """
        Should not be called directly, use
        """
        self._raw_client = _RPCClientRaw(host)
        self.password = password
        self.connected = False

    async def connect(self):
        if not self.connected:
            await self._raw_client.connect()
            self.connected = True

    def authorize(self, password: str):
        """
        Post-initialization authorization
        """
        self.password = password

    async def _authorize(self):
        """
        Authenticate at the server
        """
        await self._raw_client.send(ET.Element(TAG.AUTH1))
        nonce = (await self._raw_client.receive()).text
        auth2 = ET.Element(TAG.AUTH2)
        nonce_hash = ET.SubElement(auth2, TAG.NONCE_HASH)
        salted = nonce + self.password
        nonce_hash.text = md5(bytes(salted, encoding="UTF8")).hexdigest()
        await self._raw_client.send(auth2)
        return (await self._raw_client.receive()).tag == TAG.AUTHORIZED
