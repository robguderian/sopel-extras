import random
import sopel

# in ~/.sopel/default.cfg
# [insults]
# insultpath=/path/to/insults.txt
def configure(config):
    config.add_option('insults','insultpath','path to insults file')

@sopel.module.commands('insult')
def insult(bot, trigger):
    """ Spouts a random insult from insults.txt """
    insults_array = []
    if hasattr(bot.config,'insults') and hasattr(bot.config.insults,'insultpath'):
        with open(bot.config.insults.insultpath, "r") as insults:
            for i in insults.readlines():
                insults_array.append(i)
        bot.say(random.choice(insults_array))
    else:
        bot.say("Insults not configured. Add configuration.")
