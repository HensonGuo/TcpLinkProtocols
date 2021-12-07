from threading import Thread
from socket import socket
from common.request import PacketRequest
from common.packet import PacketTypes
from common.constants import *


class ClientConnection(Thread):
    rc4Readerkey = "123456789"
    rc4Senderkey = "123456789"

    def __init__(self, connection:socket, adress:str):
        super(ClientConnection, self).__init__()
        self._connection = connection
        self._adress = adress

    def run(self) -> None:
        while True:
            self.handle_request()

    def sendRc4Key(self):
        req = PacketRequest(SID_APP, CID_RC4KEY,
                            [[self.rc4Readerkey, PacketTypes.string],
                             [self.rc4Senderkey, PacketTypes.string]])
        self._connection.send(req.serialize())

    def handle_request(self):
        request = self._connection.recv(1024)
        print(request.decode())
        http_response = b"""\
        HTTP/1.1 200 OK

        Hello, World!
        """
        self._connection.send(http_response)

    def close(self):
        self._connection.close()