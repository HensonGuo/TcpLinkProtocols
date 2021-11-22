import socket                        #网络编程需要用到socket模块

client = socket.socket()             #创建一个客户端
client.connect(('127.0.0.1', 8008))  #连接服务端

client.send(b'nice to meet you')     #向服务端发消息
s_info = client.recv(1024)           #接受服务端发来的消息
print(s_info)
client.close()                       #关闭客户端