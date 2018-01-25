from threading import Thread
from terminaltables import AsciiTable
import sqlite3 as sql
import md5
import socket


class config:
    DB_PATH = "data.db"
   
    @staticmethod
    def create_table(table_name):
        db = sql.connect(config.DB_PATH)
        c = db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS {} (usr_name,usr_pass)""".format(table_name))
        c.close()
        db.close()
    

    @staticmethod
    def show_db():
        datas = []
        config.create_table('user')
        db = sql.connect(config.DB_PATH)
        c = db.cursor()
        c.execute("""SELECT * FROM user""")
        data = c.fetchall()
        
        for i in data:
            datas.append(i)

        c.close()
        db.close()
        
        return datas

    @staticmethod
    def list_users():
        users = []
        config.create_table('user')
        db = sql.connect(config.DB_PATH)
        c = db.cursor()

        c.execute("""SELECT usr_name FROM user""")

        data = c.fetchall()

        for i in data:
            users.append(i[0])

        c.close()
        db.close()

        return users

    @staticmethod
    def check_user(name):                               
        for i in config.list_users():                                   if i == .name:                                                  return True                                             else:                                                           return False



class Login:

    def __init__(self,usr_name,usr_pass):
        self.db = sql.connect(config.DB_PATH)
        self.c = self.db.cursor()
        config.create_table('user')

        self.usr_name = usr_name
        self.hash_pass = md5.new(usr_pass).hexdigest()

    
        
    def check(self):
        self.c.execute("""SELECT * FROM user WHERE usr_name = ? AND usr_pass = ? """,(self.usr_name,self.hash_pass))

        query = self.c.fetchone()


        self.c.close()
        self.db.close()

        if query:
            return True
        else:
            return False

class Register:

    def __init__(self, usr_name, usr_pass):
        self.name = usr_name
        self.passw = md5.new(usr_pass).hexdigest()

        db = sql.connect(config.DB_PATH)
        c = db.cursor()
        config.create_table('user')
        c.execute("""INSERT INTO user VALUES (?, ?)""",(self.name,self.passw))
        db.commit()

        c.close()
        db.close()



class Server():

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.host = host
        self.port = port
        self.run = (self.host,self.port)

    def bind(self):
        self.socket.bind(self.run)
        self.socket.listen(2)
        t1 = Thread(target = self.accept)
        t1.start()


    def accept(self):
        while True:
            c, a= self.socket.accept()
            print "Connected -- {}".format(str(a))
            t2 = Thread (target = self.recvforlogin, args = (c, a))
            t2.daemon = True
            t2.start()


    def recv(self,c,a):
        while True:
            data = c.recv(1024)
            if data == "":
                pass

            elif data == "quit":
                c.close()

            else:
                return data
    
    def send(self, msg,  c, a):
        c.send(msg)


    def recvforlogin(self, c, a):
        self.send('User Name : ' ,c ,a)
        usr_name = self.recv(c,a)
        self.send('Password : ', c, a)
        usr_pass = self.recv(c,a)

        check = Login(usr_name,usr_pass).check()

        if check:
            print "Login {} from {}".format(usr_name,str(a))
            self.send('Succesfull' , c, a)

        else:
            print "Fail login from {}".format(str(a))
            self.send('Failed login' , c,a)
            self.send(' Did you register ? (e/h)' , c, a)
            ques = self.recv(c,a)

            if ques == "e":
                self.send('Register User Name: ',c,a)
                rg_name = self.recv(c,a)
                self.send('Register Pass: ',c,a)
                rg_pass = self.recv(c,a)
                
                Register(rg_name, rg_pass)
                print 'Register user {} -- {}'.format(rg_name,str(a))
                self.send('You are registered !',c,a)
                self.send(' Turn login page (e/h)',c,a)
                turn = self.recv(c,a)

                if turn == "e":
                    self.recvforlogin(c,a)

                else:
                    pass
                

            else:
                print "Exit User {}".format(str(a))
                self.send('Bye Bye',c,a)
                c.close()
            
