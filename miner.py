import sopel
import requests
import json

from threading import Timer

timer_time = 60 * 60
URL = "https://api.nanopool.org/v1/eth/user/0xfc02b7ef373ca35f5e67c9267d8dc687c3b01124"

def setup(bot):
    get_status(bot)

def get_status(bot):
    bot.memory['mine_timer'] = Timer(timer_time, get_status, args=[bot])
    bot.memory['mine_timer'].start()

def say_status(bot):
  try:
    req = requests.get(URL)
    j = json.loads(req.text)
    bot.say("Current {:.2f}, 1 hour: {:.2f}, 3 hour: {:.2f}, balance: {:.2f}".format(
      float(j['data']['hashrate']),
      float(j['data']['avgHashrate']['h1']),
      float(j['data']['avgHashrate']['h3']),
      float(j['data']['balance'])), '#farmlink')
  except:
    bot.say("derp", "#farmlink")



@sopel.module.commands('mine')
def mine(bot, trigger):
    say_status(bot)
