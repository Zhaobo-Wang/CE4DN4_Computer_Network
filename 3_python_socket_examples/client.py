import socket

# 创建Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接到服务器
client_socket.connect(('localhost', 12345))

# 发送请求
client_socket.send("请问现在的天气如何？".encode())

# 接收响应
response = client_socket.recv(1024).decode()
print("收到的回复:", response)

# 关闭连接
client_socket.close()
