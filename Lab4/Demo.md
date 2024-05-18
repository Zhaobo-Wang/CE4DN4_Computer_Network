Demo 顺序



启动server端

###### & C:/Users/wangz/AppData/Local/Programs/Python/Python310/python.exe d:/McMaster/4DN4/Lab4/lab4_v2.py -r server

The server print CRDS is listening on port: 5000



__________________________________________________________________________________________________________________

启动client端 (client 1) 

###### & C:/Users/wangz/AppData/Local/Programs/Python/Python310/python.exe d:/McMaster/4DN4/Lab4/lab4_v2.py -r client



As you can see right now it is with Prompt 

" Enter Command > "

If I type with 

###### connect 127.0.0.1 5000

(this IP address will bind to our server side, and make a connection)

-----------------------------------------

启动client端 (client 2)

**& C:/Users/wangz/AppData/Local/Programs/Python/Python310/python.exe d:/McMaster/4DN4/Lab4/lab4_v2.py -r client**



**connect 127.0.0.1 5000**

(multiple connection is working for server)

______________________________________________________________________________________________________________

First I will show that 

###### getdir

###### makeroom JimboWang 239.0.0.1 5000

###### makeroom Jimbo 239.0.0.2 5000

###### makeroom Apple 239.0.0.3 5000

###### getdir

###### deleteroom Apple

###### getdir

Show that server side also print

---------------------------------------------------------------------

Next I will show that set client name 

I define all the name in the beginning for anonymous

with name command

Client Terminal 1:

**name Peter**

Client Terminal 2:

###### name Mike

This command sets the name that is used by the client when chatting

-----------------------------------------------------------

Next we can let them enter chat room

Client Terminal 1:

###### chat JimboWang

Client Terminal 2:

###### chat JimboWang



I change the command line prompt so that it is clear show when chat mode has been entered.



All chat messages will be automatically preffxed with the name (Peter and Mike)



Text typed at the command prompt is sent over the chat room. 

Text received from the chat room is output on the command line.

--------------------------------------------------------------------------------------------------------------

Now we can exit the chat by typing

###### exit_chat

As you see the prompt change to the "Enter command:"

-----------------------------------------------------------------

Now we can type bye

###### bye

As you see the prompt change to the "Enter command:"

This closes the client-to-CRDS connection, returning the user to the main command prompt.

The server should output that the connection hasbeen closed.

We can reconnect if we needed
