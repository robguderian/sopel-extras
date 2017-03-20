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

def checkNotifications(bot, trigger, user):
    channel = trigger.sender
    if channel in NOTIFICATIONS and user in NOTIFICATIONS[channel]:
        for message in NOTIFICATIONS[channel][user]:
            prMessage = message
            NOTIFICATIONS[channel][user].remove(message)
            bot.say("Notification for " + user + ": " + prMessage)
        del NOTIFICATIONS[channel][user]

def printHelp(bot):
    bot.say("Notifier:")
    bot.say("usage: ")
    bot.say("   .notify <nick> <message> - adds a message to give to user the next time they say something.")

@sopel.module.commands('notify')
def do_notify(bot, trigger):
    channel = trigger.sender
    if channel in CHANNELS:
        words = trigger.group(2).split(' ')
        if words[0] != trigger.nick:
            notify(channel, words[0],
                    trigger.group(2).replace(words[0], "", 1))
            bot.say('Added note for ' + words[0] + '.')

@sopel.module.commands('notifyhelp')
def notifyhelp(bot, trigger):
    printHelp(bot)

@sopel.module.thread(False)
@sopel.module.rule('(.*)')
@sopel.module.priority('low')
def note(bot, trigger):
    if trigger.sender in CHANNELS:
        checkNotifications(bot, trigger, trigger.nick)
