from PyQt5 import QtCore, QtNetwork
from common.crypt import RC4
from common.request import Request
from common.response import PacketResponse
from common.packet import PacketTypes
from common.logger import getLogger
from common.constants import *


class TcpLink(QtCore.QObject):
    sigRespData = QtCore.pyqtSignal(object)
    sigConnectResult = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(TcpLink, self).__init__(parent)
        self._logger = getLogger("client")

        self._tcpSocket = QtNetwork.QTcpSocket(self)
        self._tcpSocket.readyRead.connect(self._onDataReadyRead)
        self._tcpSocket.error.connect(self._onDisplayError)
        self._tcpSocket.connected.connect(self._onConnected)
        self._tcpSocket.disconnected.connect(self._onDisconnected)

        self._cryptSender:RC4 = None
        self._cryptReader:RC4 = None
        self._isConnected = False
        self._callbacks = {}

    def connectToHost(self, ip, port):
        self._ip = ip
        self._port = port
        if self._tcpSocket.state in [QtNetwork.QTcpSocket.ConnectingState, QtNetwork.QTcpSocket.ConnectedState]:
            return
        self._tcpSocket.abort()
        self._tcpSocket.connectToHost(self._ip, self._port)

    def close(self):
        self._isConnected = False
        self._cryptSender = None
        self._cryptReader = None
        if self._tcpSocket:
            self._tcpSocket.close()

    def send(self, request:Request, callback=None):
        if not self._isConnected:
            self._logger.warn("not connect!")
            return

        if callback:
            self._callbacks[request.key()] = callback

        buffer = request.serialize()
        if self._cryptSender:
            buffer = self._cryptSender.crypt(buffer)
        bytes = QtCore.QByteArray().append(buffer)
        self._tcpSocket.writeData(bytes)

    def setCryptSender(self, rc4key=''):
        if not rc4key:
            self._cryptSender = None
        else:
            self._cryptSender = RC4(rc4key)
        return 0

    def setCryptReader(self, rc4key=''):
        if not rc4key:
            self._cryptReader = None
        else:
            self._cryptReader = RC4(rc4key)
        return 0

    def _onConnected(self):
        self._isConnected = True
        self._logger.info("Connected")
        self.sigConnectResult.emit(True)

    def _onDisconnected(self):
        self._isConnected = False
        self._logger.info("Disconnected")
        self.close()
        self.sigConnectResult.emit(False)

    def _onDataReadyRead(self):
        while True:
            if self._tcpSocket.bytesAvailable() <= 0:
                return
            if self._cryptReader:
                tagLength = 4
                request = self._tcpSocket.read(tagLength)
                buffer = self._cryptReader.crypt(request)
                length = int.from_bytes(buffer, byteorder='little')
                leftLength = length - tagLength
                if leftLength > 0:
                    request = self._tcpSocket.read(leftLength)
                    buffer = self._cryptReader.crypt(request)
            else:
                buffer = self._tcpSocket.read(4)
                length = int.from_bytes(buffer, byteorder='little')
                buffer = self._tcpSocket.read(length - 4)

            self._logger.debug(buffer)
            resp = PacketResponse(buffer)

            if resp.key() in self._callbacks:
                callback = self._callbacks[resp.key()]
                callback(resp)
                del self._callbacks[resp.key()]

            self.sigRespData.emit(resp)

    def _onDisplayError(self, socketError):
        if socketError == QtNetwork.QAbstractSocket.RemoteHostClosedError:
            reason = "socketError={} RemoteHostClosedError".format(socketError)
        elif socketError == QtNetwork.QAbstractSocket.HostNotFoundError:
            reason = "socketError={}, HostNotFoundError".format(socketError)
        elif socketError == QtNetwork.QAbstractSocket.ConnectionRefusedError:
            reason = "socketError={}, ConnectionRefusedError".format(socketError)
        else:
            reason = "socketError={}".format(self._tcpSocket.errorString())
        self._logger.info("_onDisplayError {}".format(reason))
        self._isConnected = False
        self.sigConnectResult.emit(False)