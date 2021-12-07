from threading import Thread
from socket import socket, SOL_SOCKET, SO_KEEPALIVE, SIO_KEEPALIVE_VALS
from common.request import PacketRequest
from common.packet import PacketTypes
from common.response import PacketResponse
from common.constants import *
from common.logger import getLogger
from common.crypt import RC4
import json


class ClientConnection(Thread):
    rc4Readerkey = b"123456789"
    rc4Senderkey = b"123456789"

    def __init__(self, connection:socket, adress:str):
        super(ClientConnection, self).__init__()
        self._logger = getLogger("server")
        self._connection = connection
        self._adress = adress
        self._crytSender = RC4(self.rc4Senderkey)
        self._crytReader = RC4(self.rc4Readerkey)
        self._connection.setsockopt(SOL_SOCKET, SO_KEEPALIVE, True)
        self._connection.ioctl(
            SIO_KEEPALIVE_VALS,
            (
                1, #开启保活机制
                60*1000, #1分钟后如果对方还没反应，开始探测连接是否存在
                30*1000
            )
        )

    def run(self) -> None:
        while True:
            self.handle_request()

    def sendRc4Key(self):
        req = PacketRequest(SID_APP, CID_RC4KEY,
                            [[self.rc4Readerkey, PacketTypes.buffer],
                             [self.rc4Senderkey, PacketTypes.buffer]])
        self._connection.send(req.serialize())

    def sendMessage(self, msg):
        result = 0
        reason = ""
        req = PacketRequest(SID_APP, CID_SENDMSG,
                            [[result, PacketTypes.uint32],
                             [reason, PacketTypes.string],
                             [json.dumps({"text":msg}), PacketTypes.string]])
        buffer = self._crytSender.crypt(req.serialize())
        self._connection.send(buffer)

    def handle_request(self):
        try:
            tagLength = 4
            request = self._connection.recv(tagLength)
            buffer = self._crytReader.crypt(request)
            length = int.from_bytes(buffer, byteorder='little')
            leftLength = length - tagLength
            if leftLength > 0:
                request = self._connection.recv(leftLength)
                buffer = self._crytReader.crypt(request)
                response = PacketResponse(buffer)
                if response.sid == SID_APP and response.command == CID_SENDMSG:
                    value = response.extract([PacketTypes.string])
                    self._logger.info(f"sid: {response.sid} cid: {response.command} msg:{value}")
                    data = json.loads(value[0])
                    self.sendMessage(data.get("text"))
        except Exception as e:
            self._logger.info(e.args)
            # self.close()


    def close(self):
        self._connection.close()