########################################################################

import socket
import argparse
import sys
import pandas as pd
from cryptography.fernet import Fernet, InvalidToken


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
            print("\n")
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as msg:
            print(msg)
            sys.exit(1)
        

    def process_connections_forever(self):
        try:
            while True:  
                try:
                    self.connection_handler(self.socket.accept())               
                except KeyboardInterrupt:
                    self.socket.close()
                    sys.exit(1)                
        except Exception as msg:
            print(msg)

            
        finally:    
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        
        connection, address_port = client
        Grade_File = 'course_grades_2024.csv'
        data = pd.read_csv(Grade_File)
        self.print_whole_csv(data)
        self.print_client_info(address_port[0],address_port[1])

        while True:
            try:

                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)

                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")                    
                    connection.close()
                    break

                recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                student_ID = self.extract_student_id(recvd_str)

                if len(student_ID) != 7 or not student_ID.isdigit():
                    id_error_str = (f"invalid student number, correct student id should contain 7 digits \n"
                                    f"Echo Message: {recvd_str}")
                    connection.sendall(id_error_str.encode(Server.MSG_ENCODING))
                    print("User not found \n")

                else:

                    student_ID = int(student_ID)
                    student_data = data[data['ID Number'] == student_ID]

                    if student_data.empty:
                        print("User not Found \n")
                        print("Closing client connection ... ")
                        connection.close()
                        break
                        #try:
                        #    encryption_key = self.find_encryption_key(data, student_ID)
                        #    if encryption_key is None:
                        #        raise ValueError(f"No encryption key found for student ID {student_ID}")
                        #    connection.sendall(encryption_key.encode(Server.MSG_ENCODING))
                        #except Exception as e: 
                        #    print(f"{e}")
                        #    error_message = str(e).encode(Server.MSG_ENCODING)
                        #    connection.sendall(error_message)

                    else:
                        print(f"User {student_ID} Found, Received {recvd_str[7:]} command from client \n")
                        encryption_key = self.find_encryption_key(data, student_ID)
                        #connection.sendall(encryption_key.encode(Server.MSG_ENCODING))

                        if "GMA" in recvd_str:
                            GMA = self.calculate_GMA(data)
                            GMA_bytes = str(f"Fetching Midterm Average: {GMA}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GMA_bytes)
                            connection.sendall(encryption_message_bytes)
                        elif "GL1A" in recvd_str:
                            GL1A = self.calculate_GL1A(data)
                            GL1A_bytes = str(f"Fetching Lab 1 Average: {GL1A}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GL1A_bytes)
                            connection.sendall(encryption_message_bytes)           
                        elif "GL2A" in recvd_str:
                            GL2A = self.calculate_GL2A(data)
                            GL2A_bytes = str(f"Fetching Lab 2 Average: {GL2A}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GL2A_bytes)
                            connection.sendall(encryption_message_bytes)
                        elif "GL3A" in recvd_str:
                            GL3A = self.calculate_GL3A(data)
                            GL3A_bytes = str(f"Fetching Lab 3 Average: {GL3A}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GL3A_bytes)
                            connection.sendall(encryption_message_bytes)  
                        elif "GL4A" in recvd_str:
                            GL4A = self.calculate_GL4A(data)
                            GL4A_bytes = str(f"Fetching Lab 4 Average: {GL4A}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GL4A_bytes)
                            connection.sendall(encryption_message_bytes)
                        elif "GEA" in recvd_str:
                            GEA = self.calculate_GEA(data)
                            GEA_bytes = str(f"Fetching Exam Average: {GEA}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GEA_bytes)
                            connection.sendall(encryption_message_bytes)
                        elif "GG" in recvd_str:
                            GG_str = ''
                            for column in data.columns:
                                if column not in ['Name', 'ID Number', 'Key']:
                                    grade_value = student_data.iloc[0][column]
                                    GG_str += f"{column} = {grade_value}, " 
                            GG_str = GG_str[:-2]
                            GG_bytes = str(f"Getting grades: {GG_str}").encode(Server.MSG_ENCODING)
                            encryption_message_bytes = self.encrypted_bytes(encryption_key,GG_bytes)
                            connection.sendall(encryption_message_bytes)
                        else:
                            echo_str = f"Echo Message: {recvd_str}"
                            connection.sendall(echo_str.encode(Server.MSG_ENCODING))
                            print("User input bad request \n")

            except KeyboardInterrupt:
                #print()
                #print("Closing client connection ... ")
                #connection.close()
                sys.exit(1)

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

    def find_encryption_key(self,grade,student_id):
        student_data = grade[grade['ID Number'] == student_id]

        if not student_data.empty:
            return student_data.iloc[0]['Key']
        else:
            return None
        
    def encrypted_bytes(self,encryption_key,GA_bytes):

        encryption_key_bytes = encryption_key.encode(Server.MSG_ENCODING)
        fernet = Fernet(encryption_key_bytes)
        encryption_message_bytes = fernet.encrypt(GA_bytes)
        return encryption_message_bytes

    def print_whole_csv(self,data):

        print("-" * 72)
        print("Data read from CSV file:")
        data_str = ""
        for index, row in data.iterrows():
            for column in data.columns:
                grade_value = row[column]
                data_str += f"{column} = {grade_value}, " 
        data_str = data_str[:-2] +"\n"
        print(data_str)

    def print_client_info(self,addr,port):
        print("-" * 72)
        print(f"connections recieved from {addr} on port {port}")
        print("\n")
        
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
            print("Now, you can input your (studentID+Your request Grade) \n")
            print("For example, 1803933GMA")
            print("\n")
            
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        
        while True:
            self.input_text = input("Input: ")
            if self.input_text != "":
                student_id = self.input_text[:7]
                print("command entered: ", self.input_text)
                
                Grade_File = 'Client_key_info.csv'
                data = pd.read_csv(Grade_File)               
                
                student_id = int(student_id)
                filtered_row = data[data['ID Number'] == student_id]
                
                if not filtered_row.empty:
                    self.key = filtered_row['Key'].values[0]
                    #print(f"Key Value for ID {student_id}: {self.key}")
                #else:
                    #print(f"No matching rows found for ID {student_id}.")
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
            if len(self.key) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)
            # first key is encrpyted
            if "contain 7 digits" in self.key:
                print(self.key)
                self.socket.close()
                sys.exit(1)                
            elif "No encryption" in self.key:
                print(self.key)
                self.socket.close()
                sys.exit(1)
            else:
                encryption_key = self.key  
                self.fernet = Fernet(encryption_key)      
        
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            try:
                decrypted_message_bytes = self.fernet.decrypt(recvd_bytes)
                decrypted_message = decrypted_message_bytes.decode(Server.MSG_ENCODING)
                print(f"Decrypted_message: \n{decrypted_message}")
                print("\n")
            except InvalidToken:
                print("Decryption fail! Invalid key\n")
                

#           recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
#           print(recvd_str)

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






