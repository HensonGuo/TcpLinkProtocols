import socket                        #网络编程需要用到socket模块

client = socket.socket()             #创建一个客户端
client.connect(('127.0.0.1', 8008))  #连接服务端

while True:
    s_info = client.recv(1024)           #接受服务端发来的消息
    s_info = s_info.decode(encoding='utf-8')
    print(s_info)
    if s_info == 'bye':  # 如果服务端发送的消息为bye，回复bye，结束循环
        client.send(b'bye')
        print('bye_1')
        break
    info = input('>>>')  # 输入数据，编码并发送给服务端
    info = info.encode('utf-8')
    client.send(info)
client.close()                       #关闭客户端