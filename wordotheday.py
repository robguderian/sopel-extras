import sopel

import os
import urllib2
import string
import random
from subprocess import check_output
from threading import Timer


from bs4 import BeautifulSoup

# cache of usable word list. 1 word per line.
cache_dir = '/tmp/wotdcache'
timer_time = 600

def setup(bot):
    reset(bot)

def reset(bot):
    broadcast_new_word(bot)
    bot.memory['wotd'] = get_new_word()
    print bot.memory['wotd']
    bot.memory['wotd_timer'] = Timer(timer_time, lost_wotd, args=[bot])

def broadcast_new_word(bot):
    for c in bot.channels.keys():
        bot.say('Generating new word of the day!', c)

def broadcast_word(bot):
    for c in bot.channels.keys():
        bot.say('Word of the day was %s.'%bot.memory['wotd'], c)

def lost_wotd(bot):
    broadcast_word(bot)
    bot.memory['wotd'] = get_new_word()
    bot.memory['wotd_timer'] = Timer(timer_time, lost_wotd, args=[bot])

def reload_cache():
    dictionary = load_dictionary()
    book = load_doc()
    # write this to a file
    a = []
    in_both = dictionary.intersection(book)
    with open(cache_dir, 'w') as f:
        while len(in_both):
            f.write(in_both.pop() + "\n")

def load_dictionary():
    d = set ()
    with open("/usr/share/dict/web2") as f:
        # load the whole file
        lines = f.readlines()
        for l in lines:
            d.add(l.lower().strip())
    return d

def load_doc():
    # load a book, return 1 word per line
    book = set()
    response = urllib2.urlopen('http://localroger.com/prime-intellect/mopiall.html')
    soup = BeautifulSoup(response, 'html.parser')
    for l in soup.text.split('\n'):
        for w in l.split():
            as_lower = w.lower().strip()
            if as_lower not in book:
                book.add(as_lower)
    return book

def load_cache():
    a = []
    with open(cache_dir) as f:
        for l in f.readlines():
            a.append(l.strip())
    return a
 
def get_new_word():
    if not os.path.exists(cache_dir):
        reload_cache()
    words = load_cache()
    return random.choice(words)

@sopel.module.rule('(.*)')
def checkword(bot, trigger):
    if trigger.group(1):
        words = trigger.group(1).split()
        # take punctuation off each word
        cleaned = [str(x).translate(None, string.punctuation).lower() for x in words]
        if bot.memory['wotd'] in cleaned:
            bot.say("you win")
            bot.memory['wotd_timer'].cancel()
            reset(bot)
