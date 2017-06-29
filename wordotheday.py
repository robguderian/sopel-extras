import sopel

import string
import random
from subprocess import check_output

# TODO: change to sopel.memory
wotd = 'butts'

# TODO: return an exception
def get_new_word():
    with open("/usr/share/dict/web2") as f:
        # load the whole file
        lines = f.readlines()
        return random.choice(lines)

 

@sopel.module.rule('(.*)')
def checkword(bot, trigger):
    if trigger.group(1):
        words = trigger.group(1).split()
        # take punctuation off each word
        cleaned = [str(x).translate(None, string.punctuation).lower() for x in words]
        if wotd in cleaned:
            bot.say("you win")
            bot.say(get_new_word())


