#pylint: disable=redefined-outer-name
#pylint: disable=broad-except

import sys
import socket
import time
import re

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
        self.socket   = None
        # self.logger   = Logger()
        self.userinfo = User('myusername','myhostname','myservername','myrealname')
        self.nickname = 'myfirstircconnection'
        self.channels = ['#testingircconnect']

    def connect(self, host, port):

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            self.NICK(self.nickname)
            self.USER(self.userinfo)

            for chan in self.channels:
                self.JOIN(chan)

            self.PRIVMSG('#testingircconnect', 'hiiii')

            running = True
            while running:
                recv = self.socket.recv(4096).decode('utf-8')
                self.recv(recv)

        except Exception as e:
            self.socket.close()
            print(
                type(e).__name__,          # TypeError
                __file__,                  # /tmp/example.py
                e.__traceback__.tb_lineno  # 2
            )
            sys.exit(1)
    def send(self, text, encoding='utf-8'):
        message = (text + IRC.CRLF).encode(encoding)
        self.socket.send(message)
        print(f'[{time.asctime()}]: {message}')
    def recv(self, messages):
        print(f'[{time.asctime()}]: {messages}', end='')
        if len(messages) > 0:
            messages = re.sub(r'[\r\n]', '', messages)
            prefix, command, args = IRC.parsemsg(messages)
            self.irc_handle_command(prefix, command, args)

    @staticmethod
    def parsemsg(s):
        # https://github.com/twonds/twisted/blob/master/twisted/words/protocols/irc.py
        prefix = ''
        trailing = []
        if not s:
            sys.exit(f"Could not parse empty line {s}")
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args

    @staticmethod
    def parseprefix(prefix):
        match = re.match(r'(?P<name>[^ ]+?)\!(?P<ident>[^ ]+?)@(?P<host>.+)', prefix)
        group = match.groupdict()
        if len(group) == 3:
            return group
        return False

    def NICK(self, nickname):
        self.send(f'NICK {nickname}')
    def USER(self, userinfo):
        self.send(f'USER {userinfo.username} {userinfo.hostname} {userinfo.servername} {userinfo.realname}')
    def JOIN(self, channel):
        self.send(f'JOIN {channel}')
    def PRIVMSG(self, to, message):
        self.send(f'PRIVMSG {to} :{message}')

    def irc_PING(self, prefix, args):
        if len(args) > 0:
            self.send(f'PONG {args[0]}')
    def irc_JOIN(self, prefix, args):
        who = self.parseprefix(prefix)
        if who.nickname == self.nickname:
            pass
    def irc_PRIVMSG(self, prefix, args):
        mode = 'channel' if args[0][0].strip() == '#' else 'private'
        user = IRC.parseprefix(prefix)
        if user:
            print(f'User: {user} used command {args}')
            if '!kill' in ''.join(args):
                self.socket.close()
                sys.exit()

    def irc_handle_command(self, prefix, command, args):
        print(f'''
            \rprefix : {prefix}
            \rcommand: {command}
            \rargs   : {args}
        ''')
        method = getattr(self, f'irc_{command}', None)
        if method: method(prefix, args)
        else: print(f'Could not run the command: irc_{command}')

class Bot(IRC):
    def __init__(self):
        IRC.__init__(self)

# irc = Bot()
# irc.connect('chat.freenode.net', 6667)

# messages = ''':orwell.freenode.net 372 myfirstircconnec :- #freenode and using the '/who freenode/staff/*' command. You may message
# :orwell.freenode.net 372 myfirstircconnec :- any of us at any time. Please note that freenode predominantly provides
# :orwell.freenode.net 372 myfirstircconnec :- assistance via private message, and while we have a network channel the
# :freenode-connect!bot@freenode/utility-bot/frigg NOTICE myfirstircconnec :Welcome to freenode. To protect the network all new connections will be scanned for vulnerabilities. This will not harm your computer, and vulnerable hosts will be notified.
# :freenode-connect!bot@freenode/utility-bot/frigg PRIVMSG myfirstircconnec :☺VERSION☺
# :myfirstircconnec!~myusernam@ppp-2-85-246-179.home.otenet.gr JOIN #testingircconnect
# :orwell.freenode.net 353 myfirstircconnec @ #testingircconnect :myfirstircconnec @studenttest1
# :orwell.freenode.net 366 myfirstircconnec #testingircconnect :End of /NAMES list.
# PING :orwell.freenode.net
# :myfirstircconnec!~myusernam@ppp-2-85-246-179.home.otenet.gr QUIT :Ping timeout: 240 seconds
# ERROR :Closing Link: ppp-2-85-246-179.home.otenet.gr (Ping timeout: 240 seconds)'''
