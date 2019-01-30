import sopel
import requests
import json
import sys
import time

from threading import Timer

timer_time = 60* 60 * 6
URL = "https://api.nanopool.org/v1/eth/user/0xfc02b7ef373ca35f5e67c9267d8dc687c3b01124"
TRADEURL = "https://api.quadrigacx.com/v2/ticker?book=eth_cad"

def setup(bot):
    bot.memory['mine_timer'] = Timer(timer_time, get_status, args=[bot])
    bot.memory['mine_timer'].start()

def get_status(bot):
    time.sleep(30)
    say_status(bot)
    bot.memory['mine_timer'] = Timer(timer_time, get_status, args=[bot])
    bot.memory['mine_timer'].start()

def say_status(bot):
  try:
    req = requests.get(URL)
    print "nanopool"
    print req.text
    j = json.loads(req.text)
    req = requests.get(TRADEURL)
    print "trade"
    print req.text
    t = json.loads(req.text)
    print(j)
    cads = "Unavailable"
    try:
        value = float(t['ask'])
        cadsnum = value * float(j['data']['balance'])
        cads = '{:.2f}'.format(cadsnum)
    except:
        pass
    bot.say("Curr {:.1f}, 3 hr: {:.2f}, 12 hr: {:.2f}, bal: {:.4f}/C${}".format(
      float(j['data']['hashrate']),
      float(j['data']['avgHashrate']['h3']),
      float(j['data']['avgHashrate']['h12']),
      float(j['data']['balance']),
      cads),
      '#farmlink')
  except ValueError as e:
      bot.say("Malformed JSON for miner check. API down?", "#farmlink")
      print("error with printing miner status")
      print(e)
      print(sys.exc_info()[0])
  except Exception as e:
    bot.say("derp", "#farmlink")
    print(e)
    print(sys.exc_info()[0])



@sopel.module.commands('mine')
def mine(bot, trigger):
    say_status(bot)
