from PyQt5 import QtWidgets
from client.tcp_link import TcpLink


class MainWidget(QtWidgets.QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()
        self.setWindowTitle("客户端")
        self._tcpLink = TcpLink(self)
        self._initUI()

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

    def _onConnBtnClicked(self):
        self._tcpLink.connectToHost('127.0.0.1', 8008)
        # self._tcpLink.connectToHost('192.168.42.9', 5100)

    def _onDisConnBtnClicked(self):
        self._tcpLink.close()

    def _onSendBtnClicked(self):
        self._tcpLink.sendJson(1, 1, {"text":self._editArea.toPlainText()})


if __name__ == "__main__":
    import sys, os
    os.environ["debug"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())