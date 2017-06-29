import random
import re
import sopel
import math

@sopel.module.rule('.*\$(\d+).*')
def convert_to_ammo(bot, trigger):
    ammo_prices = { ".223": 0.75,
                    "7.62x39": 0.18,
                    ".22": 0.13,
                    ".22 subsonic": 0.35,
                    "7.62x54": 1.3,
                    "7.62x51": 1.4,
                    "12G Slugs": 2,
                    "12G Target Loads": 0.36
                  }
    caliber = random.choice(ammo_prices.keys())
    as_int = int(trigger.group(1))
    number_possible = int(math.floor(as_int / ammo_prices[caliber]))
    bot.say("For $%d you could have gotten a box of %d %s"%(as_int, number_possible, caliber))
