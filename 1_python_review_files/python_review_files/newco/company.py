#!/usr/bin/env python3

"""An example module for creating Company objects. The Company object
includes an employees dictionary that includes person objects.

"""

########################################################################

import argparse
from person import *

########################################################################

class Company:

    def __init__(self, name, employee_database_file):
        """
        这是 Company 类的构造函数。它初始化一个新的 Company 对象。
        参数 name 是公司的名称。
        参数 employee_database_file 是存储员工数据的文件的路径。
        self.employees 是一个空字典，用来存储公司员工的信息。
        self.next_employee_id 设置为 1000，作为员工 ID 的起始值。
        """

        self.name = name

        self.employee_database_file = employee_database_file

        self.employees = {}

        self.next_employee_id = 1000 

        # 调用 self.import_employee_database() 方法来从文件中读取并处理员工数据。
        self.import_employee_database()

    def import_employee_database(self):
        # 此方法负责导入和处理员工数据库

        # 它调用 read_and_clean_database_records 方法来读取和清理数据库记录
        self.read_and_clean_database_records()

        # 使用 parse_employee_records 方法来解析每条记录
        self.parse_employee_records()

        # 使用 create_employee_dictionary 方法来创建员工字典
        self.create_employee_dictionary()      

        # 设置 self.next_employee_id 为当前最大的员工 ID 加一
        try:
            self.next_employee_id = 1 + max(self.employees.keys())
        except ValueError:
            pass

    def read_and_clean_database_records(self):
        # 从文件中读取员工记录，清理记录中的空格和空行

        # 如果文件不存在，会创建一个新文件

        try:
            file = open(self.employee_database_file, "r")
        except FileNotFoundError:
            print("Creating database: {}". format(self.employee_database_file))
            file = open(self.employee_database_file, "w+")
       

        self.cleaned_records = [clean_line for clean_line in
                                [line.strip() for line in file.readlines()]
                                if clean_line != '']
        """
        line.strip() for line in file.readlines()

        file.readlines() 读取文件中的所有行，返回一个包含每行内容的字符串列表
        line.strip() 对于每行，去除前后的空白字符（如空格、制表符、换行符）
        这个内部列表推导式返回一个新的列表，其中每个元素都是清理过的行       
        """

        file.close()
         


    def parse_employee_records(self):
        """解析清理过的员工记录"""

        # 将cleaned_recorded中每行分割成员工 ID、名和姓，然后存储在 self.employee_list 中
        try:
            self.employee_list = [
                (int(e[0].strip()), e[1].strip(), e[2].strip()) for e in
                [e.split(',') for e in self.cleaned_records]]
        except Exception:
            print("Error: Invalid people name input file.")
            exit()

    def create_employee_dictionary(self):
        """为每个员工创建 Person 对象并添加到 self.employees 字典中"""

        for employee in self.employee_list:
            # Try to make a new Employee object. First check if we are given
            # first and last names.
            try:
                # 字典的键是员工 ID，值是 Person 对象。
                id_number, fname, lname = employee

                new_person = Person(first_name=fname, last_name=lname)

                self.add_employee(int(id_number), new_person)

            except Exception:
                # We caught an exception. Give up and complain.
                print("Error: Name \"{}\" is not fully specified.".format(new_person))
                self.ask_to_save_database()                



    def add_employee(self, id_number=None, person=None):
        """向公司添加一个新员工。"""

        # 如果提供了 id_number，则使用它；否则，使用 self.next_employee_id 作为员工 ID。person 参数是一个 Person 对象。
        if id_number:
            self.employees[id_number] = person
        else:
            self.employees[self.next_employee_id] = person
            self.next_employee_id += 1

    def delete_employee(self, employee_id):
        #根据提供的 employee_id 删除一个员工。
        
        del self.employees[employee_id]

    def size(self):
        # 返回公司的员工数量
        return(len(self.employees))

    def get_employee_name_list(self):
        # 返回包含所有员工名字的列表
        return list(self.employees.values())

    def print_employees(self):
        # 打印公司所有员工的详细信息。
        print("\nEmployees: (Size: {})\n".format(self.size()))
        for id, p in self.employees.items():
            print("id: {} First Name: \"{}\" Last Name: \"{}\""
                  .format(id, p.first_name, p.last_name))
        print()

    def ask_to_save_database(self):
        # 提示用户是否保存员工数据库
        answer = input("Save database? (y/N): ")
        if answer == "y":
            try:
                file = open(self.employee_database_file, "w")
                for key in self.employees.keys():
                    # Create a CSV record for the database.
                    record = str(key) + "," + \
                             self.employees[key].first_name + "," + \
                             self.employees[key].last_name + "\n"
                    file.write(record)
            finally:
                file.close()
        
    def enter_new_employees(self):
        # 允许用户通过控制台输入添加新员工。

        self.print_employees()        
        while True:

            # Prompt the user for a new employee first name.
            fname = input("First name (\"q\" to quit): ").strip()
            # Restart the loop if a blank line is entered.            
            if not fname:
                continue
            # We are finished if a "q" is entered.
            elif fname == "q":
                self.ask_to_save_database()
                break

            # Prompt the user for a new employee last name.            
            lname = input("Last name (\"q\" to quit): ").strip()
            # Restart the loop if a blank line is entered.
            if not lname:
                continue
            # We are finished if a "q" is entered.
            elif lname == "q":
                self.ask_to_save_database()
                break

            try:
                # Create an object for the provided name. And add it
                # to the employee list.
                new_person = Person(first_name=fname, last_name=lname)
                self.add_employee(person=new_person)
                self.print_employees()
            except Exception:
                # We caught an exception. Give up and complain.
                print("Error: Name is not properly specified.")

    def remove_employees(self):
        # 允许用户通过控制台输入删除员工。

        while True:
            self.print_employees()
            # Prompt the user for an employee's id.
            employee_id = input("Delete employee ID: (\"q\" to quit): ").strip()
            # Restart the loop if a blank line is entered.                
            if not employee_id:
                continue
            # We are finished if a "q" is entered.            
            elif employee_id == "q":
                self.ask_to_save_database()
                break
            try:
                # Try to delete this employee. 
                self.delete_employee(int(employee_id))
                self.print_employees()
            except Exception:
                # We caught an exception. Give up and complain.
                print("Error: Employee ID error.")



if __name__ == "__main__":

    ####################################################################    
    # If invoked directly as a script, create a default company and
    # import its employee database.

    # Create a default company name.
    COMPANY_NAME = "Default Incorporated"

    # Define the default employee database file.
    EMPLOYEE_FILE = "./default_employee_database.txt"

    # Print out a 72 character divider line.
    print("-" * 72)

    # Create a new company and import its database.
    company = Company(COMPANY_NAME, EMPLOYEE_FILE)
    print("Company Name: \"{}\".".format(company.name))

    # Print out a 72 character divider line.
    print("-" * 72)

    ####################################################################
    # Use argparse module.
    
    functions = {
        'add':    company.enter_new_employees,
        'delete': company.remove_employees,
        'view':   company.print_employees,
        'size': company.size
    }

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--function',
                        choices=functions, 
                        help='view, add or delete default company employees',
                        required=True, type=str)

    args = parser.parse_args()
    functions[args.function]()

########################################################################


        
