import os
import sys
import time
import requests
import json
import threading
import re
import argparse
import pickle


def beautifyTEXT(message):
	pass

class Reddit:
	def __init__(self):
		self.options = {
			'subreddits' : [
				'WorldNews',
				'LadiesofScience',
				'labrats',
				'science', 
				'ScienceFacts', 
				'EverythingScience', 
				'ScienceHumour',
				'scientificresearch',
				'ProgrammerHumor',
				'physicsjokes',
			],
			'limit'      : 1,
			'interval'   : 10, #minutes
		}
		self.posts = []

	def notifier(self, bot):
		time.sleep(12)
		while(True):
			for subreddit in self.options['subreddits']:
				link    = 'https://www.reddit.com/r/%s/new/.json?limit=%s' % (subreddit, self.options['limit'])
				req     = requests.get(link, headers = {'User-agent': 'Chrome'})
				theJSON = json.loads(req.text)

				for post in theJSON['data']['children']:
					postID = subreddit + '_' + post['data']['id']

					if(post['data']['stickied']): continue
					if(postID in self.posts): continue

					if len(post['data']['title']) >= 200:
						post['data']['title'] = post['data']['title'][0: 200] + '...'

					self.posts.append(postID)

					title = '•\x036 ' + post['data']['title'] + '\x0f • '
					url   = '\x032' + post['data']['url']

					bot.msg(bot.mainchan, title + url)

				time.sleep(2)
			time.sleep(60 * self.options['interval'])
			if( len(self.posts) == 300): self.posts = self.posts[-50]

	def set_limit(self, limit): self.options['limit'] = limit
	def get_limit(self): return self.options['limit']

	def set_time(self, seconds): self.options['interval'] = seconds
	def get_time(self): return self.options['interval']

	def subreddit_add(self, subreddits):
		for subreddit in subreddits:
			if(subreddit not in self.options['subreddits']):
				self.options['subreddits'].append(subreddit)

	def subreddit_rem(self, subreddits): 
		for subreddit in subreddits:
			if(subreddit in self.options['subreddits']):
				self.options['subreddits'].remove(subreddit)

	def subreddit_get(self, subreddit, table, limit): # FIX
		link    = 'https://www.reddit.com/r/%s/%s/.json?limit=%s' % (subreddit, table , limit)
		req     = requests.get(link, headers = {'User-agent': 'Chrome'})
		theJSON = json.loads(req.text)
		title   = '• \x036' + theJSON['data']['children'][0]['data']['title'] + '\x0f •'
		url     = ' \x032'  + theJSON['data']['children'][0]['data']['url']
		return title + url

	def subreddit_list(self): 
		return str(self.options['subreddits'])

def setup(bot):
	bot.reddit = Reddit()
	t = threading.Thread(target=bot.reddit.notifier, args=(bot,))
	t.daemon = True
	t.start()

def run(bot, info):
	
	parser = argparse.ArgumentParser(description='Reddit')
	parser.add_argument('-limit', '--limit', nargs='?', type=int, const=1)
	parser.add_argument('-time',  '--time',  nargs='?', type=int, const=10)

	parser.add_argument('-subreddit-add', '--subreddit-add', nargs='+', default="")
	parser.add_argument('-subreddit-rem', '--subreddit-rem', nargs='+', default="")
	parser.add_argument('-subreddit-get', '--subreddit-get', nargs='?', default="")
	parser.add_argument('-subreddit-list', '--subreddit-list', action='store_true')

	parser.add_argument('-items', '--items', nargs='?', type=int, default=1, const=1)
	parser.add_argument('-table', '--table', nargs='?', type=str, default="")

	args  = parser.parse_args(info['msg'].split()[1:])
	print (args)

	# if(bot.members.is_logged(info['user'])):
	if args.limit: bot.reddit.set_limit(args.limit)
	if args.time : bot.reddit.set_time(args.time)

	if args.subreddit_add: bot.reddit.subreddit_add(args.subreddit_add)
	if args.subreddit_rem: bot.reddit.subreddit_rem(args.subreddit_rem)
	if args.subreddit_get: 
		msg = bot.reddit.subreddit_get(args.subreddit_get, args.table, args.limit)
		bot.msg(bot.mainchan, msg)
	if args.subreddit_list:
		msg = bot.reddit.subreddit_list()
		bot.msg(bot.mainchan, msg)





