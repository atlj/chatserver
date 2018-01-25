__version__ = 0.2
__author__ = "Atli"

import socket, os, json, time, random
from threading import Thread
from core import *
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
from time import ctime
directory = os.path.dirname(os.path.realpath(__file__))


config.DB_PATH = "data.db"
config.create_table("user")
threads = []
clientlist = []
addrlist = []
os.system("clear")
connected = 0
looplist = []
listenmode = False
newer = 0
freshpool = []
roomlist = {}
threadnumber = 0
connectedlist = {}

def prepare(socketobject, message):
    time = ctime().split(" ")
    time = time[3]
    strng = message
    todump = {"msg":strng, "nick":"SV", "ctime":time}
    socketobject.send(bytes(json.dumps(todump), "UTF-8"))


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
    idle = "login"
    prepare(c, "Welcome to Atli server login or register")
    print("{} has just connected.".format(addr))
    print(str(connected)+"/"+str(maxnumber))
    addrlist.append(addr)
    clientlist.append(c)
    while 1:
        try:
            receive = c.recv(1024).decode("utf-8")
        except Exception as e:
            pass
        if not receive == "":
            try:
                recved = json.loads(receive)
                received = recved["msg"]
            except Exception as e:
                pass
        if "msg" in received:
            if idle == "suspend" or idle == "room":
                splitted = received.split(" ")
                nicktosend = splitted[1]
                messagetosend = splitted[2:]
                try:
                    connectedlist[nicktosend].send(bytes(json.dumps({"msg" : " ".join(messagetosend), "nick":nick+"(msg)"}), "UTF-8"))
                except Exception as e:
                    prepare(c, "Couldnt found any user named "+nicktosend) 
        if idle == "login":
            try:
                if received == "register":
                    prepare(c, "please enter a nickname")
                    try:
                        registerusername = c.recv(1024).decode("utf-8")
                        registerusername = json.loads(registerusername)
                        registerusername = registerusername["msg"]
                        if config.check_name(registerusername):
                            prepare(c, "Nick seems OK please enter a password")
                            try:
                                registerpass = c.recv(1024).decode("utf-8")
                                registerpass = json.loads(registerpass)
                                registerpass = registerpass["msg"]
                                if not registerpass == "" or " ":
                                    value_a = random.randrange(1, 20)
                                    value_b = random.randrange(1, 20)
                                    solve = value_a + value_b
                                    prepare(c, "CAPTCHA: "+str(value_a)+" + "+str(value_b)+" =  ?")
                                    try:
                                        captcha = c.recv(1024).decode("utf-8")
                                        captcha = json.loads(captcha)
                                        captcha = captcha["msg"]
                                        if captcha == str(solve):
                                            Register(registerusername, registerpass)
                                            prepare(c, "new user "+registerusername+" is registered.")
                                            userlist[registerusername]= registerpass
                                            filer = open(directory+"/userlist", "w")
                                            filer.write(json.dumps(userlist))
                                            filer.close()
                                            print("newuser "+registerusername+" has just registered")
                                        else:
                                            prepare(c, "Captcha solve is not true")
                                    except Exception as e:
                                        pass
                                else:
                                    prepare(c, "password cant be empty")
                            except Exception as e:
                                pass
                        else:
                            prepare(c, "Nick is already taken")
                    except Exception as e:
                        pass
                if received == "login":
                    prepare(c, "Please enter your username")
                    user = json.loads(c.recv(1024).decode("utf-8"))
                    user = user["msg"]
                    prepare(c, "OK need password")
                    passwd = json.loads(c.recv(1024).decode("utf-8"))
                    passwd = passwd["msg"]
                    try:
                        val_a = random.randrange(1, 20)
                        val_b = random.randrange(1, 20)
                        solve = val_a + val_b
                        prepare(c, "CAPTCHA: "+str(val_a) + " + "+ str(val_b) + " = ?")
                        try:
                            glen = c.recv(1024).decode("utf-8")
                            glen = json.loads(glen)
                            glen = glen["msg"]
                            if glen == str(solve):                   
                                if Login(user,passwd).check():
                                    prepare(c, "Succesful Login please enter to a room (join roomname)")
                                    nick = user
                                    idle = "suspend"
                                else:
                                    prepare(c, "Incorrect Authantication Details")
                            else:
                                prepare(c, "CAPTCHA solve is not correct")
                        except Exception as e:
                            prepare(c, "Incorrect Authantication Details")
                    except Exception as e:
                        pass
            except Exception as e:
                pass
                    
        if idle == "suspend":
            connectedlist[nick] = c
            try:
                wishedroom = json.loads(receive)
                wishedroom = wishedroom["msg"]
                if "join" in wishedroom:
                    wishedroom = wishedroom.split(" ")[-1]
                    try:
                        room = wishedroom
                        roomlist[room].append(c)
                        idle = "room"
                        prepare(c, "You re now in "+wishedroom+" channel")
                        print("{} has just joined to {} channel".format(addr, room))
                    except Exception as e:
                        room = wishedroom
                        roomlist[room] = []
                        roomlist[room].append(c)
                        prepare(c, "You re now in "+wishedroom+" channel")
                        print("{} has just joined to {} channel".format(addr, room))
                        idle = "room"
                    
            except Exception as e:
                pass
        if idle == "room":
            if not "msg" in received:
                if not "join" in received:
                    try:
                        gelen = receive
                        gelen = json.loads(gelen)
                        gelen["nick"] = nick
                        if listenmode == True:
                            print("{} > {} > {}".format(nick, room, gelen["msg"]))
                        if gelen["msg"] == "bye":
                            idle = "suspend"
                            roomlist[room].remove(c)
                            prepare(c, "You have just leaved the room")
                            print("{} has just disconnected from {} channel".format(addr, room))
                        gelen = json.dumps(gelen)              
                        for users in roomlist[room]:
                            if not users == c:
                                users.send(bytes(gelen, "UTF-8"))
                    except Exception as a:
                        pass
        
        if receive == "":
            c.close()
            print("{} has just disconnected.".format(addr))
            connected = connected - 1
            print(str(connected)+"/"+str(maxnumber))
            clientlist.remove(c)
            addrlist.remove(addr)
            threader("yes")
            if idle == "suspend":
                del connectedlist[nick]
            if idle == "room":
                del connectedlist[nick]
                roomlist[room].remove(c)                
            break
            
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
