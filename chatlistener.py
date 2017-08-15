__version__ = 0.2
__author__ = "Atli"

import socket, os, json
from threading import Thread
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
import pickle
threads = []
clientlist = []
addrlist = []
os.system("clear")
connected = 0
looplist = []
userlist = {"atli":"atlariseverim", "easyly":"easyly"}
listenmode = False
newer = 0
freshpool = []
threadnumber = 0

def getipandport():
    global ip
    global port
    global maxnumber
    ip = input("desired ip> ")
    try:
        port = int(input("desired port> "))
        maxnumber = int(input("capacity> "))
    except ValueError:
        getipandport()

def bindserver():
    try:
        s.bind((ip, port))
        s.listen(4)
    except Exception as e:
        print(e)
        main()

def threader(addone):
    global newer
    if addone == "no":
        for i in range(maxnumber):
            t = Thread(target = accept, args=())
            threads.append(t)
            threads[i].start()
        print("maximum capacity is:",maxnumber)
        print("[*]\tlistening\t"+ip+":"+str(port))
    if addone == "yes":
        t = Thread(target = accept, args=())
        freshpool.append(t)
        freshpool[newer].start()
        newer += 1
    t2 = Thread(target=status, args=())
    t2.start()

def accept():
    global clientlist
    global connected
    admin = False
    c, addr = s.accept()
    connected += 1
    print("{} has just connected.".format(addr))
    print(str(connected)+"/"+str(maxnumber))
    c.send(bytes(json.dumps({"msg":"WELCOME TO ATLI SERVER","nick":"SV"}), "utf-8"))
    addrlist.append(addr)
    clientlist.append(c)
    while 1:
        receive = c.recv(1024).decode("utf-8")
        if not receive == "":
            try:
                recved = json.loads(receive)
                received = recved["msg"]
            except Exception as e:
                pass

        if receive == "":
            c.close()
            print("{} has just disconnected.".format(addr))
            connected = connected - 1
            print(str(connected)+"/"+str(maxnumber))
            clientlist.remove(c)
            addrlist.remove(addr)
            threader("yes")
            break
        elif received == "login":
            c.send(bytes(json.dumps({"msg":"please enter your username:", "nick":"SV"}), "utf-8"))
            user = c.recv(1024).decode("utf-8")
            user = json.loads(user)
            user = user["msg"]
            c.send(bytes(json.dumps({"msg":"ok need password","nick":"SV"}), "utf-8"))
            passwd = c.recv(1024).decode("utf-8")
            passwd = json.loads(passwd)
            passwd = passwd["msg"]
            try:
                if userlist[user] == passwd:
                    admin = True
                    c.send(bytes(json.dumps({"msg":"login completed welcome {}".format(user), "nick":"SV"}), "utf-8"))
                    print("{} is logged in.".format(user))
                else:
                    c.send(bytes(json.dumps({"msg":"incorrect authentication details", "nick":"SV"}), "UTF-8"))
                    print("unsuccesful login attempt")
            except Exception as e:
                c.send(bytes(json.dumps({"msg":"incorrect authentication details", "nick":"SV"}), "UTF-8"))
                print("unsuccesful login attempt")
                pass
        else:
            if listenmode :
                print(recved["nick"]+" > "+received)
            for cli in clientlist:
                if not cli == c:
                    cli.send(bytes(receive, "UTF-8"))
 
def status():
    global listenmode
    inp = input("")
    if inp == "status":
        if len(addrlist) == 0:
            print("there are no connections alive")
        elif len(addrlist) == 1:
            print("1 client is connected right now:")
            print(addrlist[0])
        else:
            print("{} clients are connected right now:".format(connected)) 
            for addr in addrlist:
                print(addr)
    if inp == "kill":
        print("killing server...")
        for c in clientlist:
            c.close()
        s.close()
    if "say" in inp:
        mesaj = " ".join(inp.split(" ")[1:])
        for c in clientlist:
            c.send(bytes(json.dumps({"msg":mesaj, "nick":"SV"}), "UTF-8"))
    if inp == "listen":
        print("toggled listenmode on")
        listenmode = True
    if inp == "silence":
        print("toggled listenmode off")
        listenmode = False
    status()   
        
def main():
    global commands
    commands = ["status", "kill", "say", "listen", "silence"]
    getipandport()
    print("server will start from: "+ip+":"+str(port))
    if input("to start the server press (y)\n") == "y":    
        os.system("clear") 
        bindserver()
        print("Python Socket Based Chat Server \nCoded by:Atli github.com/atlj\nv0.1")
        print("avaliable commands: "+" ".join(commands))
        threader("no")
    else:
        main()

if __name__=="__main__":
    main()