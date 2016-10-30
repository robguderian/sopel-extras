import sopel.module

from threading import Timer

'''
RPG States
'''
RPG_REGISTER = 1
RPG_RUNNING = 2
RPG_OFF = 3

'''
game states
'''
IN_BATTLE = 1
ROAMING = 2

'''
Base class for character classes

All character classes must inherit from this class.
Sets defaults and standards, holds information about the character.
'''
class base_class():
    def __init__(self):
        self.name = name
        self.hp = 50
        self.mana = 0
        self.ac = 10

        self.load()

    '''
    class loader. Overload this function to customize the character
    '''
    def load(self):
        pass

    '''
    tryhit: see if this character is hit. Returns boolean, true if hit,
    false if not.
    DnD style, the attack roll is input
    Special character classes like thief override this, adding dodge
    TODO: Add attack type?
    '''
    def tryhit(self, attackroll):
        return attackroll >= self.ac


class figher_class(base_class):
    def load():
        self.hp = 60
        self.ac = 13

'''
Player class

Holds information about this player.
- who it is
- what class they are playing
- more?
'''
class player():
    def __init__(self, name):
        self.name = name
        self.char= None

'''
Map classes

The game's core is an n by m map that is being explored
This is implemented with an array of arrays. Each array element
is a MapCell class
'''
class Map():
    def __init__(self, n, m):
        self.grid = []
        self.n = n
        self.m = m
        for i in range(0, n):
            self.grid.append([])
            for j in range(0, m):
                self.grid[i].append(MapCell())

class MapCell():
    def __init__(self):
        self.visitable = True
        self.visited = False
        self.start = False
        self.end = False
        self.known = True
        self.doorNorth = True
        self.doorEast = True
        self.doorSouth = True
        self.doorWest = True
        self.occupants = []
    def get_icon(self):
        if self.start:
            return 's'
        if self.end:
            return 'e'
        if self.visited:
            return '.'
        if self.known:
            return '?'
        return ' '

@sopel.module.commands('startrpg')
def startrpg(bot, trigger):
    if ((bot.memory.contains('rpgstate') and bot.memory['rpgstate'] == RPG_OFF)
            or not bot.memory.contains('rpgstate')):
        bot.memory['rpgstate'] = RPG_REGISTER
        # make a new player list
        bot.memory['players'] = {}
        # gs is game state
        bot.memory['gs'] = ROAMING
        # make an nxm grid. n and m are configurable (TODO)
        bot.memory['x'] = 10
        bot.memory['y'] = 10
        bot.memory['map'] = Map(10, 10)
        bot.say('RPG now starting! Type .register to register for this game!')
        # end registration after a timeout (in seconds)
        t = Timer(60, registration_end, args=[bot])
        t.start()
    else:
        # game is running... reply, or is that spammy?
        pass

def registration_end(bot):
    if len(bot.memory['players']) == 0:
        bot.say('No one registered. Good bye')
        bot.memory['rpgstate'] = RPG_OFF
    else:
        bot.say('Registration is now closed. Welcome, '
                + ', '.join(bot.memory['players'].keys()) + '.')
        bot.memory['rpgstate'] = RPG_RUNNING

@sopel.module.commands('register')
def register(bot, trigger):
    if not bot.memory.contains('rpgstate')\
            or bot.memory['rpgstate'] != RPG_REGISTER:
        return
    # see if they are already registered
    if trigger.nick not in bot.memory['players']:
        bot.memory['players'][trigger.nick] = None
        bot.say(trigger.nick + ' is now registered.')

'''
isrunning helper function

Tells us if the game is running.
'''
def isrunning(bot):
    if bot.memory.contains('rpgstate'):
        if bot.memory['rpgstate'] == RPG_RUNNING:
            return True
    return False

def mapline(mapinfo):
   s = "+"
   for _ in range(0, mapinfo.n):
        s+= "-"
   s += '+'
   return s

@sopel.module.commands('map')
def showmap(bot, trigger):
    if isrunning(bot):
        m = bot.memory['map']
        line = mapline(m)
        bot.say(line)
        for row in m.grid:
            s = '|'
            for col in row:
                 s += col.get_icon()
            s += '|'
            bot.say(s)
        bot.say(line)

@sopel.module.commands('bail')
def bail(bot, trigger):
    if isrunning(bot):
        if trigger.nick in bot.memory['players']:
            del bot.memory['players'][trigger.nick]
            if len(bot.memory['players']) == 0:
                bot.say('Everyone quit!')
                bot.memory['rpgstate'] == RPG_OFF
