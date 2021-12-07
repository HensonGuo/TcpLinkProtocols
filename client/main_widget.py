from PyQt5 import QtWidgets
from client.server_link import ServerLink
from common.response import JsonResponse, PacketParser
from common.packet import UnPack, PacketTypes
from common.constants import *


class CustomTestResponse(metaclass=PacketParser):
    __sid__ = SID_APP
    __command__ = CID_CUSTOM_TEST
    __proto__ = (PacketTypes.custom, )
    __slots__ = ["data"]

    def getCustom(self, name, unpacket: UnPack):
        buffer = unpacket.getBuffer()
        unpacket = UnPack(buffer)
        tag = unpacket.getUint32()
        value = unpacket.getString()
        return {tag:value}


class MainWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()
        self.setWindowTitle("客户端")
        self._serverLink = ServerLink(self)
        self._initUI()
        self._initConnections()

    def _initUI(self):
        self.resize(500, 800)
        self._mainLayout = QtWidgets.QHBoxLayout()
        self._mainLayout.setContentsMargins(10, 10, 10, 10)
        self._mainLayout.setSpacing(10)
        self.setLayout(self._mainLayout)

        letfWidget = QtWidgets.QWidget(self)
        letfWidget.setFixedWidth(100)
        self._mainLayout.addWidget(letfWidget)
        self._initLeftArea(letfWidget)

        rightWidget = QtWidgets.QWidget(self)
        self._mainLayout.addWidget(rightWidget)
        self._initRightArea(rightWidget)

    def _initLeftArea(self,letfWidget):
        leftAreaLayout = QtWidgets.QVBoxLayout()
        leftAreaLayout.setContentsMargins(0, 0, 0, 0)
        leftAreaLayout.setSpacing(10)
        letfWidget.setLayout(leftAreaLayout)
        leftAreaLayout.addSpacing(10)

        self._connBtn = QtWidgets.QPushButton()
        self._connBtn.setFixedSize(100, 30)
        self._connBtn.setText(u"连接服务器")
        self._connBtn.clicked.connect(self._onConnBtnClicked)
        leftAreaLayout.addWidget(self._connBtn)

        self._disConnBtn = QtWidgets.QPushButton()
        self._disConnBtn.setFixedSize(100, 30)
        self._disConnBtn.setText(u"断开连接")
        self._disConnBtn.clicked.connect(self._onDisConnBtnClicked)
        leftAreaLayout.addWidget(self._disConnBtn)

        self._customUnpackTestBtn = QtWidgets.QPushButton()
        self._customUnpackTestBtn.setFixedSize(100, 30)
        self._customUnpackTestBtn.setText(u"自定义解包测试")
        self._customUnpackTestBtn.clicked.connect(self._onCustomUnpackTestBtnClicked)
        leftAreaLayout.addWidget(self._customUnpackTestBtn)
        leftAreaLayout.addStretch(1)

    def _initRightArea(self, rightWidget):
        rightAreaLayout = QtWidgets.QVBoxLayout()
        rightAreaLayout.setContentsMargins(10, 10, 10, 10)
        rightAreaLayout.setSpacing(10)
        rightWidget.setLayout(rightAreaLayout)

        self._editArea = QtWidgets.QTextEdit()
        rightAreaLayout.addWidget(self._editArea)

        self._sendBtn = QtWidgets.QPushButton()
        self._sendBtn.setFixedSize(100, 30)
        self._sendBtn.setText(u"发送消息")
        self._sendBtn.clicked.connect(self._onSendBtnClicked)
        rightAreaLayout.addWidget(self._sendBtn)

        rightAreaLayout.addSpacing(20)

        self._consoleTitle = QtWidgets.QLabel(self)
        self._consoleTitle.setText("控制台：")
        rightAreaLayout.addWidget(self._consoleTitle)

        self._consoleArea = QtWidgets.QTextEdit()
        self._consoleArea.setEnabled(False)
        rightAreaLayout.addWidget(self._consoleArea)

    def _initConnections(self):
        self._serverLink.addJsonHandler(SID_APP, CID_SENDMSG, self._onSendMsg)
        self._serverLink.addHandler(SID_APP, CID_CUSTOM_TEST, self._onCustomTestMsg)

    def _onConnBtnClicked(self):
        self._serverLink.link('127.0.0.1', 8008)

    def _onDisConnBtnClicked(self):
        self._serverLink.unlink()

    def _onSendBtnClicked(self):
        self._serverLink.sendJson(SID_APP, CID_SENDMSG, {"text":self._editArea.toPlainText()})

    def _onCustomUnpackTestBtnClicked(self):
        self._serverLink.sendJson(SID_APP, CID_CUSTOM_TEST, {})

    def _onSendMsg(self, response:JsonResponse):
        self._consoleArea.append(response.jsondata.get("text"))

    def _onCustomTestMsg(self, response:CustomTestResponse):
        # 统一查询频道列表配置
        self._consoleArea.append(response.data.get(10))



if __name__ == "__main__":
    import sys, os
    os.environ["debug"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())