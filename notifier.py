import sopel.module

# Dicts
NOTIFICATIONS={}
CHANNELS={'#rwlgguns'}


def notify(channel, user, message):
    if not channel in NOTIFICATIONS:
        NOTIFICATIONS[channel] = {}
    if not user in NOTIFICATIONS[channel]:
        NOTIFICATIONS[channel][user] = []
    NOTIFICATIONS[channel][user].append(message)

def checkNotifications(bot, user):
    channel = bot.channel
    if user in NOTIFICATIONS[channel]:
        for message in NOTIFICATIONS[channel][user]:
            prMessage = message
            NOTIFICATIONS[channel][user].remove(message)
            bot.say("Notification for " + user + " : " + prMessage)
        del NOTIFICATIONS[channel][user]        

def printHelp(bot):
    bot.say("Notifier:")
    bot.say("usage: ")
    bot.say("   .notify <nick> <message> - adds a message to give to user the next time they say something.")

@sopel.module.commands('notify')
def notify(bot, trigger):
    channel = bot.channel
    if channel in CHANNELS:
        words = trigger.group(2).split(' ')
        if words[1] != trigger.nick:
            notify(channel, words[1], trigger.group(2).replace(words[1], "", 1)

@sopel.module.commands('.notifyhelp')
def notifyhelp(bot, trigger):
    printHelp(bot)

@thread(False)
@rule('(.*)')
@priority('low')
def note(bot, trigger):
    if bot.channel in CHANNELS:
        checknotifications(bot, trigger.nick)
        