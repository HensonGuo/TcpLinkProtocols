from PyQt5 import QtCore
from client.tcp_link import TcpLink
from common.response import PacketResponse, JsonResponse, protocol2class
from common.request import Request, JsonRequest
from common.packet import PacketTypes
from common.logger import getLogger
from common.constants import *
import sys


class ServerLink(QtCore.QObject):

    def __init__(self, parent):
        super(ServerLink, self).__init__(parent)
        self._logger = getLogger("client")
        self._tcpLink = TcpLink(self)
        self._tcpLink.sigRespData.connect(self.handleResponse)
        self._handlers = {}
        self._jsonHandlers = {}

    def link(self, host, port):
        self._tcpLink.connectToHost(host, port)

    def unlink(self):
        self._tcpLink.close()

    @QtCore.pyqtSlot(PacketResponse)
    def handleResponse(self, response):
        key = (response.sid, response.command)
        sid, cid = key
        if (sid == SID_APP) and (cid == CID_RC4KEY):
            cryptReader, cryptSender =  response.extract([PacketTypes.buffer, PacketTypes.buffer])
            self._tcpLink.setCryptReader(cryptReader)
            self._tcpLink.setCryptSender(cryptSender)

        if key in protocol2class:
            cls = protocol2class[key]
            response = cls(response)

        handlers = self._handlers.get(key)
        if handlers is not None:
            for handler in handlers:
                try:
                    handler(response)
                except Exception as e:
                    self._logger.error(f'response callback {handler} failed {key} ==== {e}', exc_info=sys.exc_info())

        handlers = self._jsonHandlers.get(key)
        if handlers is not None:
            try:
                jsonResp = JsonResponse(response)
            except Exception as e:
                self._logger.error(f"parse json response failed {key} ==== {e}")
                return
            for handler in handlers:
                try:
                    handler(jsonResp)
                except Exception as e:
                    self._logger.error(f'response callback {handler} failed {key} ==== {e}', exc_info=sys.exc_info())

    def addHandler(self, sid: int, command: int, handler, isJson=False):
        key = (sid, command)
        if isJson:
            handlers = self._jsonHandlers.get(key)
            if handlers is None:
                self._jsonHandlers[key] = [handler]
            else:
                handlers.append(handler)
            return
        else:
            handlers = self._handlers.get(key)
            if handlers is None:
                self._handlers[key] = [handler]
            else:
                handlers.append(handler)

    def addJsonHandler(self, sid: int, command: int, handler):
        self.addHandler(sid, command, handler, True)

    def removeHandler(self, sid, command, handler):
        key = (sid, command)
        handlers = self._handlers.get(key)
        if handlers is not None:
            try:
                handlers.remove(handler)
            except ValueError:
                self._logger.error(f"remove {sid} {command} {handler}")
        handlers = self._jsonHandlers.get(key)
        if handlers is not None:
            try:
                handlers.remove(handler)
            except ValueError:
                self._logger.error(f"remove {sid} {command} {handler}")

    def send(self, request:Request, callback=None):
        self._tcpLink.send(request, callback)

    def sendJson(self, sid: int, cid: int, data: dict, callback=None):
        self.send(JsonRequest(sid, cid, data), callback)