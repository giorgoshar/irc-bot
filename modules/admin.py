import os
import sys
import time
import hashlib
import pickle
import argparse

class config:
    filename = 'admins.json'

class members:
    def __init__(self):
        self.members = {}
        self.members['Singularity'] = {
            'level' : 9,
            'pass'  : 'e10adc3949ba59abbe56e057f20f883e',
            'is_on' : False,
            'la_on' : None,
        }
        self.admins_f = config.filename

    def is_admin(self, name):
        return name in self.members.keys()
    def is_logged(self, username):
        if(username in self.members.keys()):
            return self.members[username]['is_on']
        return False
    def login(self, username, password):
        if(username in self.members.keys()):
            if(self.members[username]['pass'] == password):
                self.members[username]['is_on'] = True
                self.members[username]['la_on'] = time.asctime(time.localtime(time.time()))
    def get_all(self):
        return str(self.members.keys())
    def load(self):
        self.members = pickle.load( open( self.admins_f, "rb" ) )
    def save(self):
        pickle.dump( self.members, open( self.admins_f, "wb" ) )
    def online_users(self):
        users = []
        for user in self.members.keys():
            if(self.members[user]['is_on']):
                users.append(user)
        return str(users)

def setup(bot):
    bot.members = members()

def run(bot, info):

    cmd = info['msg'].split()[0].strip()

    if(cmd == '!admin'):

        parser = argparse.ArgumentParser(description='Admin')
        parser.add_argument('-login', '--login', nargs='?', type=str)
        parser.add_argument('-list',  '--list',  action='store_true')
        parser.add_argument('-online','--online',action='store_true')
        parser.add_argument('-save',  '--save',  action='store_true')
        args  = parser.parse_args(info['msg'].split()[1:])

        if args.login:
            password = hashlib.md5(args.login.encode('utf-8')).hexdigest()
            bot.members.login(info['user'], password)
            if(bot.members.is_logged(info['user'])):
                bot.msg(info['user'], 'Logged!')

        # Admin Commands
        if(bot.members.is_logged(info['user'])):
            if args.list:
                bot.msg(info['user'], bot.members.get_all())

            if args.online:
                bot.msg(info['user'], bot.members.online_users())

            if args.save:
                bot.members.save()
