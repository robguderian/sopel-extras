import sopel
import random
from subprocess import check_output

@sopel.module.commands('fig')
def figleter(bot, trigger):
    fonts = ['banner', 'block', 'bubble', 'digital', 'lean', 'mini', 'script', 'shadow', 'slant', 'small', 'smscript', 'smshadow', 'smslant', 'standard']
    if trigger.group(2):
        fig = check_output(['figlet', '-f', random.choice(fonts), trigger.group(2)])
        for l in fig.split("\n"):
            bot.say(l)

