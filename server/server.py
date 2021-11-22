import socket                    #网络编程需要用到socket模块

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         #创建一个用于监听连接的Socket对像（服务器端）
server.setblocking(True)         #解决服务重启时报address already in use
server.bind(('127.0.0.1', 8008)) #设置服务端的ip和端口号
server.listen()                  #开始监听

while True:
    conn, addr = server.accept()     #接受服务器端发出的消息和地址信息
    while True:
        c_info = conn.recv(1024).decode('utf-8')         #接受客户端消息并解码
        print(c_info)
        if c_info == 'bye':  # 当客户端发送bye时，服务端给客户端发送bye并结束循环
            conn.send(b'bye')
            break
        info = input('>>>').encode('utf-8')
        conn.send(info)
    conn.close()                     #关闭连接

# server.close()                   #关闭服务端