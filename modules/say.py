import os
import sys
import time



def setup(bot):
	pass

def run(bot, info):
	
	if(bot.members.is_logged(info['user'])):
		if(info['channel'].startswith('#')):
			to = info['channel']
			msg   = ' '.join(info['msg'].split()[1:])
		elif (info['channel'] == bot.nickname):
			msg  = info['msg'].split()[1]
			to   = info['user']
		else:
			print('something went wrong')
			print('INFO', info)
			print('--------------------')
		bot.msg(to, msg)
