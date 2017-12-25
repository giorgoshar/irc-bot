import os
import sys
import re
import time
import datetime
import requests
import json
import urllib
import logging
import threading
import argparse

def tinyurl(url):
    link    = 'https://tinyurl.com/api-create.php?url={}'.format(url)
    newlink = requests.get(link, headers = {'User-agent': 'Chrome'}).text
    source  = urllib.parse.urlparse(url).netloc
    return (source, newlink)

class newsapi:
    def __init__(self, apikey, sources, domains, queries):
        self.apikey  = apikey
        self.link    = 'https://newsapi.org/v2/'
        self.sources = ','.join(sources)
        self.domains = ','.join(domains)
        self.queries = ','.join([])

    def get(self, endpoint, params = {}):
        params = dict((k, v) for k, v in params.items() if v)
        params = urllib.parse.unquote(urllib.parse.urlencode(params))

        # print ('{}{}?{}&apikey={}'.format(self.link, endpoint, params, self.apikey))

        try:
            res = requests.get(
                '{}{}?{}&apikey={}'.format(self.link, endpoint, params, self.apikey),
                headers = {'User-agent':'Chrome', 'Content-Type':'application/json; charset=utf-8'}
            ).json()
            res = res if res['status'] == 'ok' else None
            return res
        except Exception as e:
            _type, _value, _traceback = sys.exc_info()
            print (_type, _value)
        return None

    def notifier(self, bot):
        time.sleep(20)
        while True:
            # 3 hours for utc
            utc  = (60 * 60) * 3
            # delay until next request
            mins = 3
            date_from = datetime.datetime.fromtimestamp(time.time() - (utc)).strftime('%Y-%m-%dT%H:%M:%S')
            date_to   = datetime.datetime.fromtimestamp(time.time() - (utc) + (60 * mins) - 1).strftime('%Y-%m-%dT%H:%M:%S')

            res = bot.newsapi.get(
                'everything',
                params = {
                    'q'        : self.queries,
                    'sortBy'   : '', # relevancy, popularity, publishedAt(default)
                    'domains'  : self.domains,
                    'from'     : date_from,
                    'to'       : date_to,
                    'language' : 'en',
                    'page'     : ''
                }
            )

            jsonfile = 'everything/everything-{}-{}.json'.format(date_from, date_to)
            jsonfile = jsonfile.replace(':', '-')

            # json.dump(res, open(jsonfile, 'w'))
            
            for n, article in enumerate(res['articles']):
                if article['description'] == None: 
                    continue

                link   = tinyurl(article['url'])
                title  = '\x032,99• ' + article['title'] + ' •\x0f'
                source = '\x036,99'   + article['source']['name']  + '\x0f'
                tlink  = '\x0311,99'  + link[1] + '\x0f'

                msg = 'Title: {} Source: {} Link: {}'.format(title, source, tlink)

                bot.msg(bot.mainchan, msg)
                time.sleep(2)

            time.sleep(60 * mins)

def setup(bot):
    sources = []
    domains = [
        # science
        'phys.org',
        'sciencenews.org',
        'sciencedaily.com',
        'sciencemag.org',
        'sciencenewsforstudents.org',
        'sci-news.com',
        'newscientist.com',
        'scientificamerican.com',
        'nasa.gov',
        'sciencealert.com',
        'discovermagazine.com',
        'nextbigfuture.com',
        'popsci.com',
        'sciencedirect.com',
        'nature.com',
        'space.com',
        'plos.org',
        'psychologicalscience.org',
        'springer.com',
        'biomedcentral.com',
        'cambridge.org',
        'wiley.com',
        'iflscience.com',
        'wired.com',
        'oup.com',
        'spaceflightnow.com',
        # community
        'quora.com',
        'reddit.com',
        '9gag.com',
        'tumblr.com',
        'xkcd.com',
        'lifehacker.com',
        # mixin
        # 'independent.co.uk',
        'huffingtonpost.com',
        'bbc.com',
        # 'telegraph.co.uk',
        # 'abc.net.au',
        # 'indiatimes.com',
        # 'foxnews.com',
        # 'cnn.com',
        # 'bbc.co.uk',
        # 'theguardian.com',
        # 'reuters.com',
        # 'nbcnews.com',
        # 'eurekalert.org',
        # 'newsnow.co.uk',
        # 'journalism.org',
        # 'manoramaonline.com',
        # 'latimes.com',
        # 'go.com',
        # 'handelsblatt.com',
        # 'gizmodo.com',
        # 'washingtonpost.com',
        # 'berkeley.edu',
        # 'timesofisrael.com',
        # 'dailywire.com',
        # 'wired.com',
        # 'teenvogue.com',
        # 'apnews.com',
        # 'bristol.ac.uk',
        # 'voanews.com',
        # 'cbslocal.com',
        # 'people.com',
        # 'bloomberg.com',
        # 'slate.com',
        # 'snopes.com',
        # 'fox26houston.com',
        # 'deadspin.com',
        # 'theconversation.com',
        # 'firstdraftnews.com',
        # 'france24.com',
        # 'thehill.com',
        # 'aljazeera.com',
    ]
    queries = []
    bot.newsapi = newsapi('API_KEY', sources, domains, queries)

    t = threading.Thread(target=bot.newsapi.notifier, args=(bot,))
    t.setDaemon(True)
    t.start()

def run(bot, data):

    cmd = data['msg'].split()[0].strip()
    if(cmd == '!news'):
        # Time to UTC
        utc = (60 * 60) * 3
        date_from = datetime.datetime.fromtimestamp(time.time() - (utc)).strftime('%Y-%m-%dT%H:%M:%S')
        date_to   = datetime.datetime.fromtimestamp(time.time() - (utc) + (60 * 3)).strftime('%Y-%m-%dT%H:%M:%S')

        cmd  = data['msg'].split()[0].strip()
        msg  = data['msg'].split()[1:]

        parser = argparse.ArgumentParser(description='newsApi')

        parser.add_argument('-top-headlines', '--top-headlines', action='store_true')
        parser.add_argument('-everything'   , '--everything'   , action='store_true')
        parser.add_argument('-feed'         , '--feed'         , action='store_true')

        parser.add_argument('-queries', '--queries', nargs='?', default=bot.newsapi.queries, type=str)
        parser.add_argument('-sources', '--sources', nargs='?', default=bot.newsapi.sources, type=str)
        parser.add_argument('-lang'   , '--lang'   , nargs='?', default='', type=str)
        parser.add_argument('-cat'    , '--cat'    , nargs='?', default='',   type=str)
        parser.add_argument('-sort'   , '--sort'   , nargs='?', default='',   type=str)
        parser.add_argument('-domains', '--domains', nargs='?', default=bot.newsapi.domains,   type=str)
        parser.add_argument('-from'   , '--from'   , nargs='?', default=date_from, type=str, dest='_from')
        parser.add_argument('-to'     , '--to'     , nargs='?', default=date_to,    type=str)
        parser.add_argument('-page'   , '--page'   , nargs='?', default='',   type=str)
        
        args = parser.parse_args(msg)

        def CheckIfOnlyOneAgrumentIsTrue(iterable):
            i = iter(iterable)
            return any(i) and not any(i)

        if not CheckIfOnlyOneAgrumentIsTrue([ args.top_headlines, args.everything, args.feed ]):
            return

        res = {}
        if args.top_headlines:
            res = bot.newsapi.get(
                'top-headlines',
                params = {
                    'sources' : args.sources,
                    'language': args.lang,
                    'q'       : args.queries,
                    'cat'     : args.cat,
                }
            )
            for n, article in enumerate(res['articles']):
                if article['description'] == None: 
                    continue
                t = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                print('[{}] Source: {}, Title: {}, Link: {}'.format(article['publishedAt'], article['source']['name'], article['title'], article['url']))

            # json.dump(res, open('top_headlines.json', 'w'))

        if args.everything:
            res = bot.newsapi.get(
                'everything', 
                params = {
                    'q'        : args.queries,
                    'sortBy'   : args.sort, # relevancy, popularity, publishedAt(default)
                    'domains'  : args.domains,
                    'from'     : args._from,
                    'to'       : args.to,
                    'language' : args.lang,
                    'page'     : args.page
                }
            )
            # jsonfile = 'everything/everything-{}-{}.json'.format(date_from, date_to)
            jsonfile = 'everything/everything-{}-{}.json'.format(args._from, args.to)
            jsonfile = jsonfile.replace(':', '-')
            # if int(res['totalResults']) == 0: return 
            # json.dump(res, open(jsonfile, 'w'))
            for n, article in enumerate(res['articles']):
                if article['description'] == None: 
                    continue

                link   = tinyurl(article['url'])
                title  = '\x032,99'  + article['title'] + '\x0f'
                source = '\x036,99'  + article['source']['name']  + '\x0f'
                tlink  = '\x0311,99' + link[1] + '\x0f'
                send   = 'Title: {}, Source: {}, Link: {}'.format(title, source, tlink)

                bot.msg(bot.mainchan, send)
                time.sleep(2)

        if args.feed:
            res = bot.newsapi.get('sources')
            for n, source in enumerate(res['sources']):
                print ('{}) Source: {}, Link: {}, Category: {}'.format(n, source['name'], source['url'], source['category']))
            # json.dump(res, open('feed.json', 'w'))