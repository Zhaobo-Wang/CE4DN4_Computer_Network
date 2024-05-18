import argparse
#这个模块用于处理命令行参数


#创建了两个类的对象
class Server:
    def __init__(self):
        print("We have created a Server object: ", self)
        pass

class Client:
    def __init__(self):
        print("We have created a Client object: ", self)    
        pass


if __name__ == '__main__':
    
    roles = {'client': Client,'server': Server}
    # 字典将字符串 'client' 和 'server' 映射到对应的类 Client 和 Server
    parser = argparse.ArgumentParser()
    # 创建一个解析器对象

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)
    # 用于添加一个命令行参数 '-r' 或 '--role'，它用于指定脚本运行的角色（服务器或客户端）

    args = parser.parse_args() 
    # 解析命令行参数

    roles[args.role]()
    # 根据命令行提供的角色名称（'client' 或 'server'）来创建相应的对象


# 如何运行这个脚本
# 运行脚本时，你需要通过命令行指定 - r 参数，后面跟上 'client' 或 'server' 来选择创建哪种对象。
# 例如，使用 python script.py - r client 将创建一个 Client 对象；使用 python script.py - r server 将创建一个 Server 对象。








