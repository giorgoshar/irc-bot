import os
import sys
import time
from urllib.parse import urlparse, parse_qs
import re

def setup(bot):
    pass

def run(bot, info):
    print (bot, info)

    # regex = r'.*(youtube.com/watch\S*v=|youtu.be/)([\w-]+).*'
    regex = r'(youtube.com/watch\S*v=|youtu.be/)([\w-]+)'
    res   = re.search(regex, info['msg'])

    if(res):
        print (res)