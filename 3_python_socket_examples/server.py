import socket

# 创建Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 绑定地址和端口
server_socket.bind(('localhost', 12345))

# 开始监听
server_socket.listen()

print("服务器启动，等待连接...")

# 接受连接
connection, address = server_socket.accept()
print(f"来自{address}的连接")

# 接收数据
request = connection.recv(1024).decode()
print("收到请求:", request)

# 发送响应
response = "今天天气晴朗"
connection.send(response.encode())

# 关闭连接
connection.close()
