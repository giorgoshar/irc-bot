import os
import time
import sys
import asyncio
import re
import threading
import unicodedata
import random
import imp
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
		self.command  = {}
		self.modules  = []
		self.bot      = bot
		self.mod_path = os.getcwd() + '\modules'
		sys.path.append(self.mod_path)

	def run(self, cmd, args):
		t = threading.Thread(target=self.command[cmd]['run'], args=(self.bot, args,))
		t.daemon = True
		t.start()

	def load(self):
		modile_flist = [f.name for f in os.scandir(self.mod_path) if f.is_file()]
		for mfname in modile_flist:
			name = mfname.split('.')[0]
			ext  = mfname.split('.')[-1]
			if(ext == 'py'):
				mod = imp.load_source(name, self.mod_path + '\\' + mfname)
				mod.setup(self.bot)
				self.command[name] = {
					'cmd' : name,
					'mod' : mod,
					'run' : mod.run,
				}
				print ('Module `%s` has been loaded' % (name))
	def reload(self):
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

	def loadModules(self):
		print ("Loading modules")
		self.modules.load()

	def connectionMade(self):
		# Load modules
		self.loadModules()
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

		# for command in self.modules.command:
		# 	match = re.compile(command['cmd'])
		# 	print (re.findall(match, msg))

		if channel == self.nickname: pass # prive
		if channel.startswith('#'):  pass # channel

		# triggers = str(Config.trigger)
		triggers = ','.join(['!', '.'])
		match_trigger = re.compile(r'(?P<command>^[' + triggers + '][^\s]+)')
		print(re.findall(match_trigger, msg))



		# prv and chan
		if msg.startswith(Config.trigger):
			cmd  = msg.split()[0].replace(Config.trigger, '').strip()
			args = msg.split()[1:]
			if cmd in self.modules.command.keys():
				self.modules.run(cmd, data)
			if cmd == 'reload':
				self.modules.reload()

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