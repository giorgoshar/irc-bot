import sys
import socket
import time

class User:
    def __init__(self, username, hostname, servername, realname):
        self.username   = username
        self.hostname   = hostname
        self.servername = servername
        self.realname   = realname

    def __repr__(self):
        return f'''
            \rusername: {self.username}
            \rhostname: {self.hostname}
            \rsrvname : {self.servername}
            \rrealname: {self.realname}
        '''

class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'a')
    def write(self, message):
        now = time.asctime()
        self.file.write(f'[{now}]: {message}\n')

class IRC:
    CRLF = '\r\n'
    def __init__(self):
        self.socket = None
        self.userinfo = User('myusername','myhostname','myservername','myrealname')
        self.nickname = 'myfirstircconnection'
        self.channels = ['#testingircconnect']

        self.logger = open('log', 'a')

    def connect(self, host, port):

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            #NICK <nickname>
            nick  = f'NICK {self.nickname}'
            self.send(nick)

            #USER <username> <hostname> <servername> <realname>
            uname = f'USER {self.userinfo.username} {self.userinfo.hostname} {self.userinfo.servername} {self.userinfo.realname}'
            self.send(uname)

            for chan in self.channels:
                channel = f'JOIN {chan}'
                self.send(channel)

            message = (f'PRIVMSG  #testingircconnect :mymessage')
            self.send(message)

            running = True
            while running:
                recv = self.socket.recv(4096).decode('utf-8')
                self.recv(recv)

        except Exception as e:
            self.socket.close()
            print(f'{host}:{port} Failed', e)
            sys.exit(1)

    def send(self, text, encoding='utf-8'):
        message = (text + IRC.CRLF).encode(encoding)
        self.socket.send(message)
        print(f'[{time.asctime()}][LEN:{len(message):>06}]: {message}', end='')

    def recv(self, messages):

        if len(messages) > 0:
            self.logger.write(messages)

        print(f'[{time.asctime()}][LEN:{len(messages):>06}]: {messages}', end='')
        messages = messages.split('\n')
        for message in messages:
            if '!kill' in message:
                self.socket.close()
                sys.exit()
            if '!say' in message:
                self.irc_PRIVMSG('#testingircconnect', 'response!~')


    def irc_NICK(self, nickname):
        self.send(f'NICK {nickname}')
    def irc_USER(self, userinfo):
        self.send(f'USER {userinfo.username} {userinfo.hostname} {userinfo.servername} {userinfo.realname}')
    def irc_JOIN(self, channel):
        self.send(f'JOIN {channel}')
    def irc_PRIVMSG(self, to, message):
        self.send(f'PRIVMSG {to} :{message}')


irc = IRC()
irc.connect('chat.freenode.net', 6667)

# Userinfo = User('myusername','myhostname','myservername','myrealname')

# print(Userinfo)
# print(repr(Userinfo))
