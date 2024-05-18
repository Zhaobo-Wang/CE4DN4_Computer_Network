#!/usr/bin/env python3

import queue

# Create a list of employee objects.

employee_list = [
    {
        "id" : 1,
        "first name" : "Mel",
        "last name"  : "Smith",
        "age" : 50,
        "employer" : "McMaster University"
    },
    {
        "id" : 2,        
        "first name" : "John",
        "last name"  : "Smith",
        "age" : 55,
        "employer" : "Costco Inc."
    },
    {
        "id" : 3,        
        "first name" : "Jane",
        "last name"  : "Jones",
        "age" : 60,
        "employer" : "Tim Hortons Inc."
    },
    {
        "id" : 4,
        "first name" : "William",
        "last name"  : "Jones",
        "age" : 65,
        "employer" : "Harvey's Inc."
    },
]        

# Create FIFO and LIFO queues
fifo_queue = queue.Queue()
lifo_queue = queue.LifoQueue()

print("Putting employees in FIFO and LIFO queues:")
for employee in employee_list:
    print("Enqueueing employee: ", employee)
    fifo_queue.put(employee)
    lifo_queue.put(employee)

print("FIFO queue size = ", fifo_queue.qsize())
print("LIFO queue size = ", lifo_queue.qsize())

print("Getting from FIFO queue:")
# Iterate over the number of items in the queue until we have gotten
# everthing.
for i in range(fifo_queue.qsize()):
    print(fifo_queue.get())

print("Getting from LIFO queue:")
# Instead, keep getting items from the queue until we get a
# queue.Empty exception. 
while True:
    try:
        print(lifo_queue.get_nowait())
    except queue.Empty:
        break




    
