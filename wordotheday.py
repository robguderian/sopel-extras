import sopel
import random
from subprocess import check_output

# TODO: change to sopel.memory
wotd = 'butts'

# TODO: return an exception
def get_new_word():
    with open("/usr/share/dict/web2a") as f:
        # load the whole file
        lines = f.readlines()
        random.choice(lines)
 

@sopel.module.commands('.*')
def checkword(bot, trigger):
    if trigger.group(2):
        words = trigger.group(2).split()
        # take punctuation off each word
        cleaned = [x.translate(None, string.punctuation).lower() for x in words]
        if woth in cleaned:
            bot.say("you win")
            bot.say(get_new_word())


