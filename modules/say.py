import os
import sys
import time
from urllib.parse import urlparse, parse_qs
import re
import requests
import json
import isodate
from ircformat import *

youtube_api_key = 'AIzaSyDevHnh3v7bec-GxCwmFkKuyd7BGUUiqYk'

def setup(bot):
    pass

def run(bot, data):
    print (bot, data)

    # regex = r'.*(youtube.com/watch\S*v=|youtu.be/)([\w-]+).*'
    regex = r'(youtube.com/watch\S*v=|youtu.be/)([\w-]+)'
    res   = re.search(regex, data['msg'])

    if(res):
        res.group()
        parsed = urlparse('https://www.' + res.group())
        link   = parse_qs(parsed.query)
        if 'v' in link:
            if len(link['v']) == 1:
                payload = {'id': link['v'][0], 'part': 'contentDetails,statistics,snippet', 'key': youtube_api_key}
                headers = {'User-agent': 'Chrome'}
                req     = requests.Session().get('https://www.googleapis.com/youtube/v3/videos', params=payload, headers=headers)
                theJSON = json.loads(req.text)
                if 'error' not in theJSON and theJSON['pageInfo']['totalResults'] != 0:
                    msg =  Style.colored('You', color = Colors.RED, bg = Colors.WHITE)
                    msg += Style.colored('Tube', color = Colors.WHITE, bg = Colors.RED)
                    msg =  Style.bold(msg) + ' '
                    msg += 'Title: ' + theJSON['items'][0]['snippet']['title']
                    msg += ' | '
                    msg += 'Lenght: ' + str(isodate.parse_duration(theJSON['items'][0]['contentDetails']['duration']))
                    msg += ' | '
                    msg += 'Views: ' + theJSON['items'][0]['statistics']['viewCount']
                    msg += ' | '
                    msg += 'Channel: ' + theJSON['items'][0]['snippet']['channelTitle']
                    bot.msg(bot.mainchan, msg)


    if(data['msg'].startswith('!say') and data['user'] == 'Singularity'):
        msg = data['msg'].split()
        msg = ''.join(msg[1:])

        bot.msg(bot.mainchan, msg)
