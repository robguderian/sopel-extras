import sopel
import random

@sopel.module.commands('woot')
def figleter(bot, trigger):
    if trigger.group(2):
        bot.say('\_(^_^)_/ %s'%trigger.group(2))
    else:
        bot.say('\_(^_^)_/')

