import sopel
import requests
import json

from threading import Timer

timer_time = 60* 60 * 6
URL = "https://api.nanopool.org/v1/eth/user/0xfc02b7ef373ca35f5e67c9267d8dc687c3b01124"
TRADEURL = "https://api.quadrigacx.com/v2/ticker?book=eth_cad"

def setup(bot):
    bot.memory['mine_timer'] = Timer(timer_time, get_status, args=[bot])
    bot.memory['mine_timer'].start()

def get_status(bot):
    say_status(bot)
    bot.memory['mine_timer'] = Timer(timer_time, get_status, args=[bot])
    bot.memory['mine_timer'].start()

def say_status(bot):
  try:
    req = requests.get(URL)
    j = json.loads(req.text)
    req = requests.get(TRADEURL)
    t = json.loads(req.text)
    value = float(t['ask'])
    cads = value * float(j['data']['balance'])
    bot.say("Curr {:.2f}, 3 hr: {:.2f}, 12 hr: {:.2f}, bal: {:.4f}/C${:.2f}".format(
      float(j['data']['hashrate']),
      float(j['data']['avgHashrate']['h3']),
      float(j['data']['avgHashrate']['h12']),
      float(j['data']['balance']),
      cads),
      '#farmlink')
  except:
    bot.say("derp", "#farmlink")



@sopel.module.commands('mine')
def mine(bot, trigger):
    say_status(bot)
