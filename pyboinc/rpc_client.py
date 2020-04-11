"""
Client making requests to RPC server
managing authentication etc
"""

from .raw_client import _RPCClientRaw
import xml.etree.ElementTree as ET
from hashlib import md5


class RPCClientError(Exception):
    pass


class TAG:
    AUTH1 = "auth1"
    NONCE = "nonce"
    AUTH2 = "auth2"
    NONCE_HASH = "nonce_hash"
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    SUCCESS = "success"
    ERROR = "error"
    GET_RESULTS = "get_results"
    GET_OLD_RESULTS = "get_old_results"
    ACTIVE_ONLY = "active_only"
    GET_PROJECT_STATUS = "get_project_status"
    GET_MESSAGE_COUNT = "get_message_count"
    GET_NOTICES_PUBLIC = "get_notices_public"
    SEQNO = "seqno"
    GET_MESSAGES = "get_messages"
    TRANSLATABLE = "translatable"
    ABORT_RESULT = "abort_result"
    PROJECT_URL = "project_url"
    NAME = "name"
    SUSPEND_RESULT = "suspend_result"
    RESUME_RESULT = "resume_result"


async def init_rpc_client(host: str, password=None):
    """
    Creates RPC Client and initiates connection to RPC Server
    """
    c = RPCClient(host, password)
    await c.connect()
    return c

def _append_project_element(root: ET.Element, project_url, name):
    url = ET.SubElement(root, TAG.PROJECT_URL)
    url.text = project_url
    name_e = ET.SubElement(root, TAG.NAME)
    name_e.text = name


def xml_to_dict(e: ET.Element):
    r = {}
    for child in e:
        if len(child) > 0:
            # recurse on elements with children
            r[child.tag] = xml_to_dict(child)
        elif child.text is not None:
            # set string value if available
            r[child.tag] = child.text
        else:
            # self closing
            r[child.tag] = True
    return r


class RPCClient:
    """
    For the content and structure of returned dicts refer to https://boinc.berkeley.edu/trac/wiki/GuiRpcProtocol#RequestsandReplies
    """

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
        if self.password is None:
            return False
        auth1 = ET.Element(TAG.AUTH1)
        nonce = (await self._request(auth1)).text
        auth2 = ET.Element(TAG.AUTH2)
        nonce_hash = ET.SubElement(auth2, TAG.NONCE_HASH)
        salted = nonce + self.password
        nonce_hash.text = md5(bytes(salted, encoding="UTF8")).hexdigest()
        return (await self._request(auth2)).tag == TAG.AUTHORIZED

    async def _request(self, req: ET.Element):
        return await self._raw_client.request(req)

    async def _request_auth(self, req: ET.Element):
        rep = self.evaluate_reply(await self._request(req))
        # if unauthorized, try again
        if rep is False:
            await self._authorize()
            rep = self.evaluate_reply(await self._request(req))
        return rep

    @staticmethod
    def evaluate_reply(reply: ET.Element):
        if reply.tag == TAG.UNAUTHORIZED:
            return False
        elif reply.tag == TAG.ERROR:
            raise RPCClientError(reply.text)
        elif reply.tag == TAG.SUCCESS:
            return True
        else:
            return reply

    async def get_results(self):
        req = ET.Element(TAG.GET_RESULTS)
        ET.SubElement(req, TAG.ACTIVE_ONLY)
        return await self._request(req)

    async def get_old_results(self):
        req = ET.Element(TAG.GET_OLD_RESULTS)
        return await self._request(req)

    async def get_project_status(self):
        req = ET.Element(TAG.GET_PROJECT_STATUS)
        return await self._request(req)

    async def get_message_count(self):
        req = ET.Element(TAG.GET_MESSAGE_COUNT)
        seqno = await self._request(req)
        return int(seqno.text)

    async def get_messages(self, seqno=0, translatable=False):
        req = ET.Element(TAG.GET_MESSAGES)
        s = ET.SubElement(req, TAG.SEQNO)
        s.text = str(seqno)
        if translatable:
            ET.SubElement(req, TAG.TRANSLATABLE)
        return await self._request(req)

    async def get_notices_public(self, seqno=None):
        req = ET.Element(TAG.GET_NOTICES_PUBLIC)
        s = ET.SubElement(req, TAG.SEQNO)
        s.text = str(seqno-1) if seqno is not None else seqno
        return await self._request(req)

    ######################################################################
    # Controlling the server
    ######################################################################

    async def abort_result(self, project_url, name):
        """
        Abort a task
        """
        req = ET.Element(TAG.ABORT_RESULT)
        _append_project_element(req, project_url, name)
        return await self._request_auth(req)

    async def suspend_result(self, project_url, name):
        """
        suspend a task
        """
        req = ET.Element(TAG.SUSPEND_RESULT)
        _append_project_element(req, project_url, name)
        return await self._request_auth(req)

    async def resume_result(self, project_url, name):
        """
        suspend a task
        """
        req = ET.Element(TAG.RESUME_RESULT)
        _append_project_element(req, project_url, name)
        return await self._request_auth(req)
