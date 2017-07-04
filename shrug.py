import sopel
import random

@sopel.module.commands('shrug')
def figleter(bot, trigger):
    if trigger.group(2):
        bot.say('\_(:/)_/ %s'%trigger.group(2))
    else:
        bot.say('\_(:/)_/')

