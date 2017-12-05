import random
import sopel

@sopel.module.rule('insult')
def insult(bot):
    """ Spouts a random insult from insults.txt """
    insults_array = []
    with open("insults.txt", "r") as insults:
        for i in insults:
            insults_array.append(i)

    bot.say(random.choice(insults_array))
