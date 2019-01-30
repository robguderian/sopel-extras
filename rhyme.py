
import sopel
import urllib2
import random
import string
import json

#https://api.datamuse.com/words?rel_rhy


# match every line
@sopel.module.rule('(.*)')
def checkword(bot, trigger):
    if random.random() > 0.99 and trigger.group(1):
        words = trigger.group(1).encode('ascii','ignore').split()
        cleaned = [str(x).translate(None, string.punctuation).lower() for x in words]
        url = 'https://api.datamuse.com/words?rel_rhy={}'.format(cleaned[-1])
        r = urllib2.urlopen(url)
        j = json.loads(r.read())
        if len(j) > 0:
            rhyme = random.choice(j)
            bot.say("The Reimer Rhymer says " + rhyme['word'])

