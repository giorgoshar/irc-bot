import os
import sys
import time
import hashlib
import pickle
import argparse
import json

class config:
    filename = 'admins.json'
    admin    = { 'Singularity' : { 'level': 9, 'pass' : 'e10adc3949ba59abbe56e057f20f883e', 'is_on' : False, 'la_on' : None } }

class members:
    def __init__(self):
        self.members = config.admin
    def is_admin(self, name):
        return name in self.members.keys()
    def is_logged(self, name):
        if name in self.members.keys():
            return self.members[name]['is_on']
        return False
    def is_level(self, name, level):
        if name in self.members.keys():
            return True if self.members[name]['level'] == level else False
        return False
    def login(self, name, password):
        if name in self.members.keys():
            if(self.members[name]['pass'] == password):
                self.members[name]['is_on'] = True
                self.members[name]['la_on'] = time.asctime(time.localtime(time.time()))
    def load(self):
        with open(config.filename, 'r') as fp:
            self.members = json.load( fp.read() )
    def save(self):
        with open(config.filename, 'w') as fp:
            data = json.dump(self.members, fp, ensure_ascii=False)
    def online(self):
        users = []
        for user in self.members.keys():
            if(self.members[user]['is_on']):
                users.append(user)
        return str(users)
    def list(self):
        return str(self.members.keys())
    def add(self, name, level, password):
        if name in self.members.keys(): return
        self.members[name] = {
            'level' : level,
            'pass'  : hashlib.md5(password.encode('utf-8')).hexdigest(),
            'is_on' : False,
            'la_on' : None
        }
        self.save()
    def rem(self, name):
        self.members.pop(name)
        self.save()

def setup(bot):
    bot.members = members()
    # bot.members.load()

def run(bot, info):

    cmd = info['msg'].split()[0].strip()
    if(cmd == '!admin'):

        parser = argparse.ArgumentParser(description='Admin')
        parser.add_argument('-login' , '--login' , nargs='?', type=str)
        parser.add_argument('-add'   , '--add'   , nargs='+')
        parser.add_argument('-rem'   , '--rem'   , nargs='?', type=str)
        parser.add_argument('-list'  , '--list'  , action='store_true')
        parser.add_argument('-online', '--online', action='store_true')
        parser.add_argument('-save'  , '--save'  , action='store_true')
        
        args  = parser.parse_args(info['msg'].split()[1:])

        if args.login:
            password = hashlib.md5(args.login.encode('utf-8')).hexdigest()
            bot.members.login(info['user'], password)
            if(bot.members.is_logged(info['user'])):
                bot.msg(info['user'], 'Logged!')

        # Admin Commands
        if(bot.members.is_logged(info['user'])):
            if args.list:
                bot.msg(info['user'], bot.members.list())

            if args.online:
                bot.msg(info['user'], bot.members.online())

            if args.save:
                bot.members.save()

            # Admin(level 9) Commands
            if args.add and bot.members.is_level(info['user'], 9):
                if (len(args.add) != 3): return
                bot.members.add(*args.add)
            if args.rem and bot.members.is_level(info['user'], 9):
                bot.members.rem(args.rem)
