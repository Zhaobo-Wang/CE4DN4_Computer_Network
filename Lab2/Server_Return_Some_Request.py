########################################################################

import socket
import argparse
import sys
import pandas as pd


class Server:


    HOSTNAME = "127.0.0.1"   
    PORT = 50000
    RECV_BUFFER_SIZE = 1024 
    MAX_CONNECTION_BACKLOG = 10
    MSG_ENCODING = "utf-8"
    SOCKET_ADDRESS = (HOSTNAME, PORT)


    def __init__(self):
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(Server.SOCKET_ADDRESS)
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:           
                self.connection_handler(self.socket.accept())
                
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            self.socket.close()
            sys.exit(1)
            
        finally:
            
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        
        connection, address_port = client
        # 读数据库data
        Grade_File = 'D:/McMaster/4DN4/Lab2/course_grades_2024.csv'
        data = pd.read_csv(Grade_File)
   
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        print(client)

        while True:
            try:

                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)

                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break

                recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                print(f"Received {recvd_str} command from client")

                if "GMA" in recvd_str:
                    GMA = self.calculate_GMA(data)
                    GMA_bytes = str(f"Fetching Midterm Average: {GMA}").encode(Server.MSG_ENCODING)
                    connection.sendall(GMA_bytes)
                elif "GL1A" in recvd_str:
                    GL1A = self.calculate_GL1A(data)
                    GL1A_bytes = str(f"Fetching Lab 1 Average: {GL1A}").encode(Server.MSG_ENCODING)
                    connection.sendall(GL1A_bytes)           
                elif "GL2A" in recvd_str:
                    GL2A = self.calculate_GL2A(data)
                    GL2A_bytes = str(f"Fetching Lab 2 Average: {GL2A}").encode(Server.MSG_ENCODING)
                    connection.sendall(GL2A_bytes)
                elif "GL3A" in recvd_str:
                    GL3A = self.calculate_GL3A(data)
                    GL3A_bytes = str(f"Fetching Lab 3 Average: {GL3A}").encode(Server.MSG_ENCODING)
                    connection.sendall(GL3A_bytes)  
                elif "GL4A" in recvd_str:
                    GL4A = self.calculate_GL4A(data)
                    GL4A_bytes = str(f"Fetching Lab 4 Average: {GL4A}").encode(Server.MSG_ENCODING)
                    connection.sendall(GL4A_bytes)
                elif "GEA" in recvd_str:
                    GEA = self.calculate_GEA(data)
                    GEA_bytes = str(f"Fetching Exam Average: {GEA}").encode(Server.MSG_ENCODING)
                    connection.sendall(GEA_bytes)
                elif "GG" in recvd_str:
                    student_ID = self.extract_student_id(recvd_str)
                    if len(student_ID) != 7 or not student_ID.isdigit():
                        id_error_str = f"invalid student number {student_ID}, correct student id should contain 7 digits"
                        connection.sendall(id_error_str.encode(Server.MSG_ENCODING))
                    else:
                        student_ID = int(student_ID)
                        student_data = data[data['ID Number'] == student_ID]
                        if student_data.empty:
                            print("User not Found")
                            empty_str = f"no data found for the student: {student_ID}"
                            connection.sendall(empty_str.encode(Server.MSG_ENCODING))
                        else:
                            print("User Found")
                            GG_str = ''
                            for column in data.columns:
                                if column not in ['Name', 'ID Number', 'Key']:
                                    grade_value = student_data.iloc[0][column]
                                    GG_str += f"{column} = {grade_value}, " 
                            GG_str = GG_str[:-2]
                            connection.sendall(str(f"Getting grades: {GG_str}").encode(Server.MSG_ENCODING))
                elif "help" in recvd_str:
                    help_str = (
                        "\n"
                        "student number is referring as 7 digits number, \n"
                        "the format should be STUDENT_ID+GMA/GEA/GL1A/GL2A/GL3A/GL4A/GG (e.x. 1803933GMA) \n"
                        "GMA is average midterm grade \n"
                        "GEA is average exam grade \n"
                        "GL1A is average Lab1 grade \n"
                        "GG is your personal grade\n"
                        "... \n"
                        "Give a try right now!\n"
                        "\n"
                    )
                    connection.sendall(help_str.encode(Server.MSG_ENCODING))
                else:
                    connection.sendall(recvd_bytes)
                    print("Sent: ", recvd_str)
                
                print("Sent: ", recvd_str)

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

    def calculate_GMA(self,grade):
        return grade['Midterm'].mean()
    
    def calculate_GEA(self,grade):
        exam_columns = ['Exam 1', 'Exam 2', 'Exam 3', 'Exam 4']
        exams = grade[exam_columns]
        total_exam_scores = exams.sum(axis=1)
        return total_exam_scores.mean()
    
    def calculate_GL1A(self,grade):
        return grade['Lab 1'].mean()
    
    def calculate_GL2A(self,grade):
        return grade['Lab 2'].mean()
    
    def calculate_GL3A(self,grade):
        return grade['Lab 3'].mean()
    
    def calculate_GL4A(self,grade):
        return grade['Lab 4'].mean()
    
    def extract_student_id(self,recvd_str):
        student_id = recvd_str[:7]
        return student_id



########################################################################


class Client:

    SERVER_HOSTNAME = "localhost"
    RECV_BUFFER_SIZE = 1024     
    


    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()

    def get_socket(self):
        try:          
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
            print("Connected to \"{}\" on port {}".format(Client.SERVER_HOSTNAME, Server.PORT))
            print("Now, you can input your (studentID+Your request Grade) or input (help) for more information denoted!")
            print("\n")
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        
        while True:
            self.input_text = input("Input: ")
            if self.input_text != "":
                break
    
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:

            self.socket.sendall(self.input_text.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
            print(recvd_str)

        except Exception as msg:
            print(msg)
            sys.exit(1)

########################################################################

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################






