import os
import time
import sys
import asyncio
import re
import threading
import unicodedata
import random
import imp
import ctypes
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl, task
from twisted.python import log
from config import Config


class MessageLogger:
    def __init__(self, file):
        self.file = file

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()

class ModuleManager:
    def __init__(self, bot):
        self.modules = []
        self.bot     = bot
        self.path    = os.getcwd() + '\modules'
        sys.path.append(self.path)
        self.load()

    def run(self, data):
        threads = []
        for module in self.modules:
            t = threading.Thread(target=module['run'], args=(self.bot, data,))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        # for t in threads:
            # t.join()

    def load(self):
        print ("Loading modules")
        self.modules = []
        for item in os.scandir(self.path):
            if item.is_file():
                _, ext = os.path.splitext(item)
                if ext == '.py':
                    name = item.name
                    mod  = imp.load_source(name, _ + ext)
                    if hasattr(mod, 'setup'): mod.setup(self.bot)
                    module = {
                        'mod'   : mod,
                        'run'  :  mod.run   if hasattr(mod, 'run'  ) else None,
                    }
                    self.modules.append(module)
                    print ('Module `%s` has been loaded' % (name))

    def reload(self):
        safe_threads = ['MainThread', 'PoolThread-twisted.internet.reactor-0']
        for thread in threading.enumerate():
            if thread.name in safe_threads:
                continue
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), ctypes.py_object(SystemExit))
        self.load()

class LogBot(irc.IRCClient):
    nickname = 'scibot'
    password = ''
    lineRate = None

    def __init__(self):
        irc.IRCClient.__init__(self)
        self.mainchan = '#testing'
        self.modules  = ModuleManager(self)
        self.raw_data = ''

    def connectionMade(self):
        # Connect to server
        irc.IRCClient.connectionMade(self)
        print ("Connected")
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[Connected at %s]" % time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[Disconnected at %s]" % time.asctime(time.localtime(time.time())))
        self.logger.close()

    def signedOn(self):
        self.join(self.factory.channel)

    def joined(self, channel):
        self.logger.log("[I have joined %s]" % self.factory.channel)

    def privmsg(self, user, channel, msg):

        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        data = {
            'event'   : 'privmsg',
            'user'    : user,
            'channel' : channel,
            'msg'     : msg,
            'raw_data': self.raw_data
        }
        self.modules.run(data)
        if(msg.startswith('!reload')):
             self.modules.reload()
        if channel == self.nickname: pass # prive
        if channel.startswith('#'):  pass # channel

    def alterCollidedNick(self, nickname):
        return nickname + str(random.randint(0, 100))

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))
    
    def userJoined(self, user, channel):
        self.logger.log("%s has joined %s" % (user, channel))

    def dataReceived(self, data):
        self.raw_data = data
        irc.IRCClient.dataReceived(self, data)

class LogBotFactory(protocol.ClientFactory):
    protocol = LogBot
    def __init__(self, channel, filename):
        self.channel  = channel
        self.filename = filename
    # def startedConnecting(self, connector):
        # print ('Connection stared', connector)
    def clientConnectionLost(self, connector, reason):
        print ("Lost connection (%s), reconnecting." % (reason))
        # connector.connect()
        sys.exit()
    def clientConnectionFailed(self, connector, reason):
        print ("Connection failed:", reason)
        reactor.stop()

class Bot(LogBotFactory):
    def __init__(self):
        LogBotFactory.__init__(self, ','.join(Config.channels), Config.logfile)

    def connect(self, hostname, port):
        reactor.connectTCP(Config.hostname, Config.port, self)
        # reactor.connectSSL(hostname, port, f, ssl.ClientContextFactory())
        reactor.run()

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    bot = Bot()

    bot.connect(Config.hostname, Config.port)