import socket                        #网络编程需要用到socket模块

client = socket.socket()             #创建一个客户端
client.connect(('127.0.0.1', 8008))  #连接服务端

while True:
    info = input('>>>').encode('utf-8')
    client.send(b'from c1:' + info)
    s_info = client.recv(1024).decode(encoding='utf-8')
    print(s_info)
    if s_info == 'bye':  # 如果服务端发送的消息为bye，回复bye，结束循环
        client.send(b'bye')
        break
client.close()                       #关闭客户端