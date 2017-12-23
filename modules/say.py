import os
import sys
import time
from urllib.parse import urlparse, parse_qs
import re
import requests
import json
import isodate
from ircformat import *

youtube_api_key = 'API_KEY'

def setup(bot):
    pass

def run(bot, data):

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
                    ytlogo_you  = Style.colored('You',  color=Colors.RED,   bg=Colors.WHITE)
                    ytlogo_tube = Style.colored('Tube', color=Colors.WHITE, bg=Colors.RED)
                    ytlogo      = Style.bold(ytlogo_you + ytlogo_tube)

                    title    = theJSON['items'][0]['snippet']['title']
                    duration = str(isodate.parse_duration(theJSON['items'][0]['contentDetails']['duration']))
                    views    = int(theJSON['items'][0]['statistics']['viewCount'])
                    channel  = theJSON['items'][0]['snippet']['channelTitle']

                    msg = '{} Title: {} Length: {} Views: {:,d} Channel: {}'.format(ytlogo, title, duration, views, channel)
                    bot.msg(bot.mainchan, msg)