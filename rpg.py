import sopel.module

from threading import Timer
import random
import re

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
Buffs and debuffs
These can stack.
'''

class BaseBuff:
    def __init__(self):
        self.name = ""
        self.melee_attack_mod = 0
        self.magic_attack_mod = 0
        self.melee_damage_mod = 0
        self.magic_damage_mod = 0
        self.melee_defense_mod = 0
        self.magic_defense_mod = 0
        # how long is this active for, in turns
        self.usage = 4
    def __str__(self):
        # there should be an action
        return " becomes COMPLETE THIS MESSAGE."

class Slow(BaseBuff):
    def __init__(self):
        BaseBuff.__init__(self)
        self.name = "Slow"
        self.melee_damage_mod = -2
        self.melee_attack_mod = -2

class Poison(BaseBuff):
    def __init__(self):
        BaseBuff.__init__(self)
        self.name = "Poison"
        self.melee_defense = -4
        self.magic_defense = -4
    def __str__(self):
        return " becomes poisoned!"

class Rage(BaseBuff):
    def __init__(self):
        BaseBuff.__init__(self)
        self.name = "Rage"
        self.melee_mod = 6
    def __str__(self):
        return " becomes enraged!"


'''
attack object

Attacks get rolled, the damage gets rolled immedately with it.
Future: we could pass damage as a closure
'''
class attack:
    def __init__(self, attacker, attack, dmg, attackmod = 0, damagemod = 0, debuff=None):
        self.attacker = attaker
        self.attack = attack + attackmod
        self.dmg = dmg + damagemod

        # on hit, add debuff
        self.debuff = debuff

'''
Base class for character classes

All character classes - that's playable and enemy classes -
must inherit from this class.
Sets defaults and standards, holds information about the character.
'''
class base_class():
    def __init__(self):
        self.name = ''
        self.maxhp = 50
        self.hp = 50
        self.mana = 0
        self.ac = 10
        self.initiative_mod = 0

        # stats for special things
        # agility for escaping
        self.agility_mod = 5

        self.player = False

        self.items = []
        self.buffs = []

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
    def tryhit(self, attackobj):
        return (attackobj.attack + self.getAttackMod() >=
                self.ac + self.getDefenseMod())

    '''
    The character has been hit
    '''
    def hit(self, bot, attack):
        totaldmg = (attack.dmg + self.getDamageMod())
        self.hp -= totaldmg
        bot.say(self.attacker.name + ' hit ' + self.name + ' for ' +
                    str(attack.dmg) + ' hp!')
        return totaldmg

    def roll_initiative(self):
        return random.randint(1,20) + self.initiative_mod

    def roll_agility(self):
        return random.randint(1,20) + self.agility_mod

    def addHP(self, amt, in_combat = False):
        if in_combat:
            self.hp += amt
        else:
            self.hp = min(self.hp + amt, self.maxhp)

    def subHP(self, amt, in_combat = False):
        self.hp -= amt
        if self.hp < 0:
            # check the game state, clean the initiative list if need be.
            if bot.memory['gs'] == IN_BATTLE:
                battle = bot.memory['battle'].clean_list()

    def item_list(self):
        return [str(v) for v in self.items]

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    '''
    Do the basic attack for this character, returns an attack object
    '''
    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,4)
        return attack(self, att, dmg, self.getAttackMod(), self.getDamageMod())

    '''
    do a special attack

    The user may specify a target (focused attack vs AOE)
    '''
    def special_attack(self, bot, target_str=None):
        pass

    def removeBuff(self, BuffClass):
        for i in reversed(range(0, len(self.buffs))):
            if type(self.buffs[i]) == BuffClass:
                self.buffs.pop(i)

    def getAttackMod(self, isMagic = False):
        mod = 0
        for buff in self.buffs:
            if isMagic:
                mod += buff.magic_attack_mod
            else:
                mod += buff.melee_attack_mod
        return mod

    def getDefenseMod(self, isMagic = False):
        mod = 0
        for buff in self.buffs:
            if isMagic:
                mod += buff.magic_defense_mod
            else:
                mod += buff.melee_defence_mod
        return mod

    def getDamageMod(self, isMagic = False):
        mod = 0
        for buff in self.buffs:
            if isMagic:
                mod += buff.magic_damage__mod
            else:
                mod += buff.melee_damage_mod
        return mod



class fighter_class(base_class):
    def load(self):
        self.maxhp = 60
        self.hp = self.maxhp
        self.ac = 13
        self.player = True
        # todo
        self.name = 'Fighter'
        self.items = [Potion(), Potion(), Potion()]

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20) + 2
        # base damage, 1d4
        dmg = random.randint(1,6)
        return attack(self, att, dmg,
                          self.getAttackMod(),
                          self.getDamageMod() )

    def special_attack(self, bot, target_str=None):
        bot.say(self.name + " charges at the monsters, slashing wildly.")
        battle = bot.memory['battle']
        for f in battle.get_baddies():
            att = attack( self,
                          random.randint(1,20) + 4,
                          random.randint(1,4) + 1,
                          self.getAttackMod(),
                          self.getDamageMod() )
            if f.tryhit(att):
                d = f.hit(att)
                bot.say(self.name + ' hit ' + f.name + ' for ' + str(d) + '!')
        battle.clean_list(bot)
        battle.next_turn(bot)

    @classmethod
    def classname(cls):
        return 'Fighter'

class healer_class(base_class):
    def load(self):
        self.maxhp = 50
        self.hp = self.maxhp
        self.ac = 12
        self.player = True
        # todo
        self.name = 'Healer'

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20) + 0
        # base damage, 1d4
        dmg = random.randint(1,4)
        return attack(self, att, dmg,
                          self.getAttackMod(),
                          self.getDamageMod() )
    def special_attack(self, bot, target_str=None):
        # TODO - add targeted healing
        bot.say(self.name + " heals the team.")
        players = bot.memory['players']
        for p in players.values():
            gains = random.randint(1,10) + 2
            p.char.hp += gains
            bot.say(p.name + ' gains ' + str(gains) + ' hp, to '
                    + str(p.char.hp) + '.')
        bot.memory['battle'].next_turn(bot)

    @classmethod
    def classname(cls):
        return 'Healer'

class mage_class(base_class):
    def load(self):
        self.maxhp = 40
        self.hp = self.maxhp
        self.ac = 12
        self.player = True
        # todo
        self.name = 'mage'
        self.items = [Potion(), Potion()]

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20) + 5
        # base damage, 1d4
        dmg = random.randint(1,10)
        return attack(self, 
                          att, dmg,
                          self.getAttackMod(),
                          self.getDamageMod() )

    def special_attack(self, bot, target_str=None):
        bot.say(self.name + " calls fire from the floor.")
        battle = bot.memory['battle']
        for f in battle.get_baddies():
            att = attack( self,
                          random.randint(1,20) + 4,
                          random.randint(1,8) + 1 ,
                          self.getAttackMod(),
                          self.getDamageMod(),
                          Slow() )
            if f.tryhit(att):
                d = f.hit(att)
                bot.say(self.name + ' hit ' + f.name + ' for ' + str(d) + '!')
        battle.clean_list(bot)
        battle.next_turn(bot)

    @classmethod
    def classname(cls):
        return 'Mage'


POSSIBLE_PLAYER_CLASSES = [fighter_class, healer_class, mage_class]

class npc(base_class):
    def do_turn(self, bot, occupants):
        # choose random opponent, use base attack
        to_attack = random.choice(occupants)
        while not to_attack.player:
            to_attack = random.choice(occupants)
        the_attack = self.base_attack()
        if to_attack.tryhit(the_attack):
            to_attack.hit(bot, the_attack)
        else:
            bot.say(self.name + ' missed ' + to_attack.name + '!')

class ogre(npc):
    def load(self):
        names = ['Zarg',
                'Brirug',
                'Urok',
                'Blokurg',
                'Erth',
                'Krowugark',
                'Grurugrok',
                'Xegekork',
                'Uikor',
                'Braekig',
                'Trurub',
                'Egut',
                'Kag',
                'Klaruk',
                'Kokork',
                'Briuzug',
                'Glaakor',
                'Kliogrut',
                'Meugut',
                'Glibigrok']
        self.name = random.choice(names) + ' the ogre'
        self.hp = 4
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,6)
        return attack(self, att, dmg)

class imp(npc):
    def load(self):
        names = ['Chil',
                'Zogro',
                'Ekjit',
                'Cyoq',
                'Alnob',
                'Truphet',
                'Trur',
                'Abqiuz',
                'Gribjir',
                'Cyox',
                'Zir',
                'Kyegmop',
                'Uphem',
                'Drom',
                'Trabqa',
                'Igban',
                'Dip',
                'Cyoklot',
                'Bibjo',
                'Cyor']
        self.name = random.choice(names) + ' the imp'
        self.hp = 2
        self.mana = 0
        self.ac = 12

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20) + 1
        # base damage, 1d4
        dmg = random.randint(1,4)
        return attack(self, att, dmg)

class goblin(npc):
    def load(self):
        names = ['Zriabs',
                'Plaq',
                'Crierd',
                'Vrord',
                'Striag',
                'Clirkog',
                'Komild',
                'Hieltial',
                'Vreelseakx',
                'Clelvakt',
                'Lielk',
                'Piolb',
                'Krard',
                'Greek',
                'Kaz',
                'Gnoilruct',
                'Brezlug',
                'Zadyct',
                'Cakneabs',
                'Briozeez']
        self.name = random.choice(names) + ' the goblin'
        self.hp = 3
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20) + 1
        # base damage, 1d4
        dmg = random.randint(1,4)
        return attack(self, att, dmg)

class troll(npc):
    def load(self):
        names = ['Makas',
                'Mohanlal',
                'Venjo',
                'Razi',
                'Zulrajas',
                'Mohanlal',
                'Tazingo',
                'Jaryaya',
                'Melkree',
                'Jojin',
                'Matuna',
                'Hamedi',
                'Ugoki',
                'Shengis',
                'Trezzahn',
                'Shaktilar',
                'Halasuwa',
                'Tedar']
        self.name = random.choice(names) + ' the troll'
        self.hp = 10
        self.mana = 0
        self.ac = 7

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,4)
        return attack(self, att, dmg)


'''
Possible monsters
'''
POSSIBLE_MONSTERS = [ogre, imp, troll, goblin]

class end_boss(npc):
    def do_turn(self, bot, occupants):
        # choose random opponent, use base attack
        to_attack = random.choice(occupants)
        while not to_attack.player:
            to_attack = random.choice(occupants)
        if random.random() > 0.5:
            the_attack = self.base_attack()
            if to_attack.tryhit(the_attack):
                to_attack.hit(bot, the_attack)
            else:
                bot.say(self.name + ' missed ' + to_attack.name + '!')
        else:
            the_attack = self.special_attack(bot)

class greater_ogre(end_boss):
    def load(self):
        names = ['Zarg',
                'Brirug',
                'Urok',
                'Blokurg',
                'Erth']
        self.name = random.choice(names) + ' the greater ogre'
        self.hp = 15
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,8)
        return attack(self, att, dmg)

    def special_attack(self, bot, target_str=None):
        bot.say('The ogre swings his massive tree-trunk like clubs in a '
                + 'wide arc hoping to hit everyone in the whole team.')
        battle = bot.memory['battle']
        for f in battle.get_goodies():
            att = attack( self,
                          random.randint(1,20) + 4,
                          random.randint(1,4) - 1 )
            if f.tryhit(att):
                f.hit(bot, att)

class phoenix(end_boss):
    def load(self):
        names = [
                'Rise',
                'Eterna',
                'Beam',
                'Inferno',
                'Luminos',
                'Dawn',
                'Torch',
                'Shine',
                'Zeal',
                'Brilliancy']
        self.name = random.choice(names) + ' the phoenix'
        self.hp = 15
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,8)
        return attack(self, att, dmg)

    def special_attack(self, bot, target_str=None):
        bot.say(self.name + ' turns into a fire state, burning everything '
                + 'in the room.')
        battle = bot.memory['battle']
        for f in battle.get_goodies():
            att = attack( self,
                          random.randint(1,20) + 4,
                          random.randint(1,4) - 1 )
            if f.tryhit(att):
                f.hit(bot, att)

class griffon(end_boss):
    def load(self):
        names = [
                'Priapus',
                'Notus',
                'Aether',
                'Phantomwings',
                'Mudbeak',
                'Dwarftail',
                'Solarnail',
                'Selena',
                'Furious',
                'Saki']
        self.name = random.choice(names) + ' the griffon'
        self.hp = 15
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,8)
        return attack(self, att, dmg)

    def special_attack(self, bot, target_str=None):
        bot.say(self.name + ' becomes airborne, flies at the team, slashing '
                + 'its talons fiercely.')
        battle = bot.memory['battle']
        for f in battle.get_goodies():
            att = attack( self, 
                          random.randint(1,20) + 4,
                          random.randint(1,4) - 1 )
            if f.tryhit(att):
                f.hit(bot, att)

class minotaur(end_boss):
    def load(self):
        names = [
                'Stampy',
                'Goebaran',
                'Gragajan',
                'Podkan',
                'Kurfaruk',
                'Kirfaruk',
                'Goerus',
                'Kirkun',
                ]
        self.name = random.choice(names) + ' the minotaur'
        self.hp = 15
        self.mana = 0
        self.ac = 10

    def base_attack(self):
        # base attack, 1d20
        att = random.randint(1,20)
        # base damage, 1d4
        dmg = random.randint(1,8)
        return attack(self, att, dmg)

    def special_attack(self, bot, target_str=None):
        bot.say(self.name + ' puts his head down, pointing his horns '
                + 'at the team and charges.')
        battle = bot.memory['battle']
        for f in battle.get_goodies():
            att = attack( self,
                          random.randint(1,20) + 4,
                          random.randint(1,4) - 1 )
            if f.tryhit(att):
                f.hit(att)

POSSIBLE_END_BOSSES = [griffon, greater_ogre, minotaur]


'''
Player class

Holds information about this player.
- who it is
- what class they are playing
- more?
'''
class player():
    def __init__(self, name, chosentype = None):
        self.name = name
        # TODO
        if chosentype is None:
            c = random.choice(POSSIBLE_PLAYER_CLASSES)
            self.char = c()
        else:
            self.char = chosentype
        self.char.name = name

'''
class battle

Holds information about the current battle
'''
class battle:
    def __init__(self, bot, cell, playerlist):
        self.cell = cell
        players = [x.char for x in playerlist.values()]
        self.combatants = cell.occupants + players
        # do inititative rolls
        self.init = [(x.roll_initiative(), x) for x in self.combatants]
        self.init.sort(key= lambda tup: tup[0], reverse=False)
        # now, sorted by initiative
        self.combatants = [x[1] for x in self.init]
        self.curr_turn = -1
        names = [x.name for x in self.combatants]
        bot.say('Fighters take initiative: ' + ', '.join(names) + ".")
        self.next_turn(bot)

    def current_turn(self):
        return self.combatants[self.curr_turn]

    def next_turn(self, bot):
        # check if it's over
        # did people die in the last attack?
        self.clean_list(bot)
        if self.complete():
            if self.won():
                bot.say('The enemies have been vanquished')
                c = bot.memory['map'].get_current_cell()
                c.occupants = []
                bot.memory['gs'] = ROAMING
                if c.end:
                    bot.say('You win! The end!')
                    bot.memory['rpgstate'] = RPG_OFF
            else:
                bot.say('All the team has died... game over')
                bot.memory['rpgstate'] = RPG_OFF
        else:
            self.curr_turn = (self.curr_turn + 1) % len(self.combatants)
            curr_fighter = self.combatants[self.curr_turn]
            if curr_fighter.player:
                bot.say('Your turn, ' + curr_fighter.name + '.')
            else:
                # pass the whole list of occupants, in case the monster is
                # confused. From there any of the occupants can be attacked.
                curr_fighter.do_turn(bot, self.combatants)
                self.clean_list(bot)
                self.next_turn(bot)
    '''
    Write the changes made during battle to memory
    '''
    def write_changes(self):
        self.cell.occupants = []
        for c in self.combatants:
            if not c.player and c.hp > 0:
                self.cell.occupants.append(c)

    def count_baddies(self):
        count = 0
        for c in self.combatants:
            if not c.player:
                count += 1
        return count

    def get_baddies(self):
        baddies = []
        for c in self.combatants:
            if not c.player:
                baddies.append(c)
        return baddies

    def get_goodies(self):
        goodies = []
        for c in self.combatants:
            if c.player:
                goodies.append(c)
        return goodies

    def try_escape(self, player):
        # modify the difficulty based on the numnber of enemies
        base_escape_difficulty = 15
        return player.roll_agility() > (base_escape_difficulty +
                                        self.count_baddies())

    def is_turn(self, name):
        return self.combatants[self.curr_turn].name == name

    def complete(self):
        # all enemies, or all players are dead
        player_count = 0
        enemy_count = 0
        for p in self.combatants:
            if p.player:
                player_count += 1
            else:
                enemy_count += 1
        return player_count == 0 or enemy_count == 0

    def won(self):
        enemy_count = 0
        for p in self.combatants:
            if not p.player:
                enemy_count += 1
        return  enemy_count == 0

    def op_attacks(self, bot):
        good = []
        bad = []
        for c in self.combatants:
            if c.player:
                good.append(c)
            else:
                bad.append(c)

        for b in bad:
            b.do_turn(bot, good)


    def clean_list(self, bot):
        # announce the death of any combatants, clean up the list
        # reminder: more than one may have died.
        # the index must be decremented for every death that's under the
        # pointer index
        for f in self.combatants:
            if f.hp <= 0:
                bot.say(f.name + ' has died.')
                if self.combatants.index(f) <= self.curr_turn:
                    self.curr_turn -= 1
                self.combatants.remove(f)

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
        # choose random start and end points
        start = (random.randint(0, n-1),
            random.randint(0, m-1))
        self.current_cell = start
        end = (random.randint(0, n-1),
            random.randint(0, m-1))
        while (start[0] == end[0] and start[1] == end[1]):
            end = (random.randint(0, n-1),
                random.randint(0, m-1))
        for i in range(0, n):
            self.grid.append([])
            for j in range(0, m):
                self.grid[i].append(MapCell(i, j))
        self.grid[start[0]][start[1]].set_start()
        endcell = self.grid[end[0]][end[1]]
        endcell.end = True
        endboss = random.choice(POSSIBLE_END_BOSSES)
        endcell.occupants = [endboss()]
        # Make random door. Check if the map is possible
        # repeat until the map is possible
        while not self.check_possible():
            self.make_random_door()

    '''
    make_random_door

    make a random door somewhere in the map.
    '''
    def make_random_door(self):
        # key on a cell, then choose a random wall
        # yes, the doors on a corner/wall cell have a higher probability
        # whatever.
        # deal with it.
        cell = (random.randint(0, self.n - 1),
                random.randint(0, self.m - 1))
        # 0 = north
        # 1 = east
        # 2 = south
        # 3 = west
        d = random.randint(0, 3)
        c = self.grid[cell[0]][cell[1]]
        if d == 0 and c.x - 1 >= 0:
            c.doorNorth = True
            self.grid[cell[0] - 1][cell[1]].doorSouth = True
        if d == 1 and c.y + 1 < self.m:
            c.doorEast = True
            self.grid[cell[0]][cell[1] + 1].doorWest = True
        if d == 2 and c.x + 1 < self.n:
            c.doorSouth = True
            self.grid[cell[0] + 1][cell[1]].doorNorth = True
        if d == 3 and c.y - 1 >= 0:
            c.doorWest = True
            self.grid[cell[0]][cell[1] - 1].doorEast = True

    '''
    Visit a cell, check neighbours.

    Mark neighbours as known, this cell as visited
    '''
    def visit_cell(self, x, y):
        self.grid[x][y].visited = True
        if self.grid[x][y].doorNorth:
            self.grid[x-1][y].known = True
        if self.grid[x][y].doorSouth:
            self.grid[x+1][y].known = True
        if self.grid[x][y].doorEast:
            self.grid[x][y+1].known = True
        if self.grid[x][y].doorWest:
            self.grid[x][y-1].known = True

    def get_current_cell(self):
        return self.grid[self.current_cell[0]][self.current_cell[1]]

    '''
    try move

    Try a move, don't move and print error on failure
    '''
    def try_move(self, bot, direction, describe = True):
        if direction is None:
            bot.say("Need a direction to move")
            return False
        d = direction.lower()
        c = self.get_current_cell()
        moved = True
        if d == 'south' and c.doorSouth:
            self.current_cell = (c.x + 1, c.y)
        elif d == 'north' and c.doorNorth:
            self.current_cell = (c.x - 1, c.y)
        elif d == 'east' and c.doorEast:
            self.current_cell = (c.x, c.y + 1)
        elif d == 'west' and c.doorWest:
            self.current_cell = (c.x, c.y - 1)
        else:
            bot.say("Can't move " + direction + ".")
            moved = False
        self.visit_cell(self.current_cell[0], self.current_cell[1])
        if describe:
            c = self.get_current_cell()
            bot.say(c.describe())
        return moved

    '''
    check_possible - ensure map has path from start to finish

    Use a backtracking algorithm to make sure that there is a clear map
    from start to finish.
    '''
    def check_possible(self):
        # start from the start
        # add all possible moves, that have not been visited
        # pop the stack, add all possible moves...
        c = self.get_current_cell()
        seen = []
        todo = [c]
        success = False
        while len(todo) > 0 and not success:
            cur = todo.pop()
            seen.append(cur)
            if cur.end:
                success = True
                print(seen)
            if cur.doorNorth:
                t = (self.grid[cur.x-1][cur.y])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorSouth:
                t = (self.grid[cur.x+1][cur.y])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorEast:
                t = (self.grid[cur.x][cur.y+1])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorWest:
                t = (self.grid[cur.x][cur.y-1])
                if not t in seen and not t in todo:
                    todo.append(t)
        return success

    '''
    print the map
    '''
    def print_map(self, bot):

        def mapline():
           s = "+"
           for _ in range(0, self.m):
                s+= "-"
           s += '+'
           return s

        line = mapline()
        bot.say(line)
        for row in self.grid:
            s = '|'
            for col in row:
                if (col.x == self.current_cell[0] and
                        col.y == self.current_cell[1]):
                    s += 'C'
                else:
                    s += col.get_icon()
            s += '|'
            bot.say(s)
        bot.say(line)

class MapCell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visitable = True
        self.visited = False
        self.start = False
        self.end = False
        self.known = False
        self.doorNorth = False
        self.doorEast = False
        self.doorSouth = False
        self.doorWest = False
        self.occupants = []
        # make n random enemies in this room.
        # exponential distributions are bursty. Most rooms will be empty
        # then some rooms will have many, few will have some.
        num_monsters = min(5, random.expovariate(0.5))
        for _ in range(0, random.randint(0,5)):
            monstertype = random.choice(POSSIBLE_MONSTERS)
            self.occupants.append(monstertype())
        # choose some features.
        # set up that we could have more than one eventually.
        self.features = []
        while random.random() > 0.5:
            self.features = random.sample(POSSIBLE_FEATURES, 1)
            # instantiate them!
            self.features = [f() for f in self.features]

    def set_start(self):
        self.start = True
        self.occupants = []

    def get_icon(self):
        if self.start:
            return 's'
        if self.end and self.visited:
            return 'e'
        if self.visited:
            return '.'
        if self.known:
            return '?'
        return ' '

    def get_exits(self):
        exits = []
        if self.doorNorth:
            exits.append('North')
        if self.doorEast:
            exits.append('East')
        if self.doorSouth:
            exits.append('South')
        if self.doorWest:
            exits.append('West')
        if len(exits) == 1:
            return 'You see an exit to the ' + ', '.join(exits) + '.'
        if len(exits) > 1:
            return 'You see exits to the ' + ', '.join(exits) + '.'

    def get_features(self):
        if len(self.features) > 0:
            names = [x.getName() for x in self.features]
            return 'You see a room with ' + ', '.join(names) + '.'
        elif random.random > 0.7:
            s = ['You see a boring room.']
            return random.choice(s)
        return None

    def get_monsters(self):
        if len(self.occupants) == 0:
            if random.random > 0.6:
                Nothing = ['The room is full of still, stale air.',
                'The room is quiet.... too quiet.',
                'Silence fills the room.',
                'The only sound in the room is the sounds of your footsteps.']
                return random.choice(Nothing)
            else:
                return None
        elif len(self.occupants) == 1:
            name = self.occupants[0].name
            Badguy = [name + " was having a nice quiet time, minding his own "
                    + "business when you walked in.",
                    "You woke " + name + " from a nap... prepare to pay!"]
            return random.choice(Badguy)
        else: # multiple monsters
            names = [x.name for x in self.occupants]
            Baddies = ['You meet ' + ', '.join(names)
                    + ". They don't look happy to meet you.",
                    " You encounter " + str(len(self.occupants)) + " monsters."
                    + " They were having dinner, and you look like a good "
                    + "addition!"]
            return random.choice(Baddies)

    def describe(self):

        l = [self.get_features(), self.get_monsters(), self.get_exits()]
        l = [x for x in l if x is not None]
        return ' '.join(l)

'''
class feature - things that can appear in rooms. Features must inherit this
class

features can be interacted with, having positive, negative and no effects
'''
class Feature():
    '''
    get effect

    what happens when this feature is interacted with?
    Passing in bot, we can see which player did the interaction, get the team,
    see if there are baddies, etc.
    Depending on the feature, the
    effect could be player-specific, or team-specific (or a random choice of
    the team, or everyone who didn't touch the feature, or....)
    '''
    def getEffect(self, bot, player):
        pass
    '''
    get info - what is this feature

    when inspected, what do we know about this feature?
    '''
    def getInfo(self):
        pass

    '''
    getName

    Get a short name for this feature to add to a list
    '''
    def getName(self):
        pass
    def __str__(self):
        return self.getName()
    def __repr__(self):
        return self.getName()

class Fountain(Feature):
    def getName(self):
        return 'a burbling fountain'
    def getInfo(self):
        return 'A fountain sits undisturbed.'

class GoodFountain(Fountain):
    def __init__(self):
        self.used = False

    def getEffect(self, bot, player):
        if self.used:
            bot.say('You get wet.')
        else:
            self.used = True
            team = bot.memory['players'].values()
            bot.say('The team feels a warm tingling...')
            in_combat = bot.memory['gs'] == IN_BATTLE
            for p in team:
                amt = random.randint(1,10)
                bot.say(p.name + ' receives ' + str(amt) + 'hp.')
                p.char.addHP(amt, in_combat)

    def getInfo(self):
        if self.used:
            return 'A blackened fountain'
        else:
            return 'A fountain sits undisturbed.'

class BadFountain(Fountain):
    def __init__(self):
        self.used = False

    def getEffect(self, bot, player):
        if self.used:
            bot.say('You get wet.')
        else:
            self.used = True
            team = bot.memory['players'].values()
            bot.say('The team feels a warm tingling... no... hot... too hot!')
            in_combat = bot.memory['gs'] == IN_BATTLE
            for p in team:
                amt = random.randint(1,6)
                bot.say(p.name + ' loses ' + str(amt) + 'hp.')
                p.char.subHP(amt, in_combat)
                if p.char.hp < 0:
                    bot.say(p.name +' dies.')

    def getInfo(self):
        if self.used:
            return 'A blackened fountain'
        else:
            return 'A fountain sits undisturbed.'

class LooseBrick(Feature):
    def __init__(self):
        # choose a random item
        possible_items = POSSIBLE_ITEMS
        possible_items.append(None)
        chosenItem = random.choice(possible_items)
        self.item = None
        if chosenItem is not None:
            self.item = chosenItem()

    def getEffect(self, bot, player):
        if self.item is not None:
            # the current player gets the item
            bot.say(player.name + ' gets a ' + self.item.getName() + '.')
            player.items.append(self.item)
        else:
            bot.say('You find spiderwebs and dust')
    def getName(self):
        return 'a loose brick'
    def getInfo(self):
        return "A brick on the wall doesn't match the rest."

class Latrine(Feature):
    def __init__(self):
        # choose a random item
        self.item = None
        if random.random() > 0.98:
            possible_items = POSSIBLE_ITEMS
            chosenItem = random.choice(possible_items)
            self.item = None
            if chosenItem is not None:
                self.item = chosenItem()

    def getEffect(self, bot, player):
        if self.item is not None:
            # the current player gets the item
            bot.say(player.name + ' gets a ' + self.item.getName() + '.')
            player.items.append(self.item)
        else:
            bot.say('You find poop. What did you expect to find?')

    def getName(self):
        return 'a latrine'

    def getInfo(self):
        return "A latrine sits in the corner. It looks like it's been used "\
                + "frequently, but never cleaned."

POSSIBLE_FEATURES = [GoodFountain, BadFountain, LooseBrick, Latrine]

class Item:
    def __init__(self):
        self.name = 'name me!'

    def use(self, bot, player):
        pass

    def getName(self):
        return self.name

    def __str__(self):
        return self.getName()

    def __repr__(self):
        return self.getName()

class Potion(Item):
    def __init__(self):
        amts = [20, 30, 50]
        self.fill_amt = random.choice(amts)
        self.name = 'potion'

    def use(self, bot, player):
        bot.say(player.name + ' uses a potion and gets ' + str(self.fill_amt)
                + 'hp.')
        player.addHP(self.fill_amt)

class Pure(Item):
    def __init__(self):
        self.name = "Pure"

    def use(self, bot, player):
        bot.say(player.name + ' uses pure on the team, removing all poison.')
        for p in bot.memory['players']:
            c = bot.memory['players'][p].char
            c.removeBuff(Poison)

POSSIBLE_ITEMS = [Potion, Pure]

@sopel.module.commands('startrpg')
def startrpg(bot, trigger):
    if ((bot.memory.contains('rpgstate') and bot.memory['rpgstate'] == RPG_OFF)
            or not bot.memory.contains('rpgstate')):
        bot.memory['rpgstate'] = RPG_REGISTER
        bot.say('RPG now starting!')
        bot.say('Building the world...')
        # make a new player list
        bot.memory['players'] = {}
        # gs is game state
        bot.memory['gs'] = ROAMING
        # make an nxm grid. n and m are configurable (TODO)
        x = 4
        y = 10
        mapsizes = trigger.group(2)
        m = None
        if mapsizes is not None:
            m = re.match('(\d+) (\d+)', mapsizes)
            if m is not None:
                x = int(m.group(1))
                y = int(m.group(2))

        bot.memory['x'] = x
        bot.memory['y'] = y
        bot.memory['map'] = Map(x, y)
        bot.say('Type .register to register for this game.')
        # end registration after a timeout (in seconds)
        t = Timer(20, registration_end, args=[bot])
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
        c = bot.memory['map'].get_current_cell()
        bot.memory['map'].visit_cell(c.x, c.y)
        bot.say(c.describe())

@sopel.module.commands('register')
def register(bot, trigger):
    if not bot.memory.contains('rpgstate')\
            or bot.memory['rpgstate'] != RPG_REGISTER:
        return
    # see if they are already registered
    if trigger.nick not in bot.memory['players']:
        if trigger.group(2) is not None and len(trigger.group(2)) >= 0:
            chosen = trigger.group(2)
            chosentype = None
            classlist = []
            for classtype in POSSIBLE_PLAYER_CLASSES:
                if classtype.classname().lower() == chosen.lower():
                    chosentype = classtype()
            if chosentype is None:
                bot.say(chosen + ' is not a valid type. Possible types '
                        + 'are ' + ', '.join(classlist) + '.')
            else:
                bot.say(trigger.nick + ' is now registered as a '
                    + chosentype.classname() + '.')
                bot.memory['players'][trigger.nick] = player(trigger.nick,
                        chosentype)

        else:
            bot.memory['players'][trigger.nick] = player(trigger.nick)
            bot.say(trigger.nick + ' is now registered as a '
                    + bot.memory['players'][trigger.nick].char.classname()
                    + '.')

'''
isrunning helper function

Tells us if the game is running.
'''
def isrunning(bot):
    if bot.memory.contains('rpgstate'):
        if bot.memory['rpgstate'] == RPG_RUNNING:
            return True
    return False

@sopel.module.commands('map')
def showmap(bot, trigger):
    if isrunning(bot) and trigger.nick in bot.memory['players']:
        bot.memory['map'].print_map(bot)

@sopel.module.commands('bail')
def bail(bot, trigger):
    if isrunning(bot):
        if trigger.nick in bot.memory['players']:
            del bot.memory['players'][trigger.nick]
            bot.say('Player ' + trigger.nick + ' quit.')
            if len(bot.memory['players']) == 0:
                bot.say('Everyone quit! Game over!')
                bot.memory['rpgstate'] = RPG_OFF

@sopel.module.commands('move')
def move(bot, trigger):
    if not isrunning(bot):
        return
    moved = False
    if (bot.memory['gs'] == ROAMING
            and trigger.nick in bot.memory['players']):
        moved = bot.memory['map'].try_move(bot, trigger.group(2))
    elif bot.memory['gs'] == IN_BATTLE:
        # don't check if a door exists. Justification: in battle, you
        # might try to escape a wrong way. You would fail.
        # first do an agility check
        if bot.memory['battle'].is_turn(trigger.nick):
            cur_player = bot.memory['players'][trigger.nick].char
            if bot.memory['battle'].try_escape(cur_player):
                moved = bot.memory['map'].try_move(bot, trigger.group(2),
                        False)
                if moved:
                    # op attacks for all!
                    bot.say('The monsters see an opportunity to attack '
                            + 'while the team is running!')
                    bot.memory['battle'].op_attacks(bot)
                    bot.say('The team escapes!')
                    bot.memory['battle'].write_changes()
                    s = bot.memory['map'].get_current_cell().describe()
                    bot.say(s)
                else:
                    bot.say('The team runs into the wall!')
            else:
                bot.say('The team fails to escape.')
                bot.memory['battle'].next_turn(bot)


    if moved:
        # check to see if there is enemies in this room.
        # if so, go into BATTLE status
        c = bot.memory['map'].get_current_cell()
        if len(c.occupants) > 0:
            bot.memory['gs'] = IN_BATTLE
            bot.memory['battle'] = battle(bot, c, bot.memory['players'])
        else:
            # if we escaped from a room, we may have to move from battle to roam
            bot.memory['gs'] = ROAMING
        # currently possible end state - you got to the end of the map, no
        # monsters to fight.
        # future, this might be possible if you can beat the end boss and leave
        # the room? Probably impossible in the future.
        if c.end and bot.memory['gs'] == ROAMING:
            bot.say('You win! The end!')
            bot.memory['rpgstate'] = RPG_OFF

@sopel.module.commands('info')
def info(bot, trigger):
    bot.say(bot.memory['map'].get_current_cell().describe())

@sopel.module.commands('attack')
def do_attack(bot, trigger):
    if (isrunning(bot)
            and bot.memory['gs'] == IN_BATTLE
            and trigger.nick in bot.memory['players']):
        # now check that it is the user's turn
        cur_battle = bot.memory['battle']
        if cur_battle.is_turn(trigger.nick):
            att = bot.memory['players'][trigger.nick].char.base_attack()
            c = bot.memory['map'].get_current_cell()
            to_attack = random.choice(cur_battle.get_baddies())
            while to_attack.player:
                # TODO - be able to choose attackee
                to_attack = random.choice(c.occupants)
            if to_attack.tryhit(att):
                to_attack.hit(bot, att)
            else:
                bot.say(trigger.nick + ' missed ' + to_attack.name + '.')
            cur_battle.clean_list(bot)
            cur_battle.next_turn(bot)

@sopel.module.commands('special')
def do_special(bot, trigger):
    if (isrunning(bot)
        and bot.memory['gs'] == IN_BATTLE
        and trigger.nick in bot.memory['players']):
        # now check that it is the user's turn
            if bot.memory['battle'].is_turn(trigger.nick):
                # pass in the bot. From there we can ge
                # all the values we need
                if len(trigger.groups()) >= 2:
                    bot.memory['players'][trigger.nick].char.special_attack(
                        bot, trigger.group(2))
                else:
                    bot.memory['players'][trigger.nick].special_attack(bot)

@sopel.module.commands('status')
def do_status(bot, trigger):
    if not isrunning(bot):
        return
    if not trigger.nick in bot.memory['players']:
        return
    for p in bot.memory['players'].values():
        itemtxt = 'Current items: ' + ', '.join(p.char.item_list()) + '.'
        if len(p.char.items) == 0:
            'No items.'
        bot.say(p.name + ': ' + str(p.char.hp) + '/' + str(p.char.maxhp)
                + 'hp, '
                + str(p.char.mana) + 'mp. '
                + ' You are a ' + p.char.classname() + '. ' + itemtxt)
    if bot.memory['gs'] == IN_BATTLE:
        bot.say('You are currently in battle, current turn: '
                + bot.memory['battle'].current_turn().name + '.')
        bot.say("You are battling:")
        for baddie in bot.memory['battle'].get_baddies():
            bot.say(baddie.name + ": " + str(baddie.hp) + ' hp.')

@sopel.module.commands('interact')
def do_interact(bot, trigger):
    if not isrunning(bot):
        return
    if not trigger.nick in bot.memory['players']:
        return
    # ok, find a thing.
    # if there is only one feature, just interact with it, without bothering
    # to check what the player typed
    cell = bot.memory['map'].get_current_cell()
    player = bot.memory['players'][trigger.nick].char
    if len(cell.features) == 0:
        bot.say('No features to check out. You pretend you were doing '
                + 'something else, other than looking at the blank wall.')
    elif len(cell.features) == 1:
        cell.features[0].getEffect(bot, player)
    else:
        found = False
        feature_names = []
        for f in cell.features:
            feature_names.append(f.getName())
            if f.getName() == trigger.group(2):
                f.getEffect(bot, player)
                break
        if not found:
            bot.say('No feature named ' + trigger.group(2) + '.')
            bot.say('Possible features: ' + ', '.join(feature_names) + '.')

@sopel.module.commands('use')
def do_use(bot, trigger):
    if not isrunning(bot):
        return
    if not trigger.nick in bot.memory['players']:
        return
    player = bot.memory['players'][trigger.nick].char
    item_names = []
    found = False
    for i in player.items:
        item_names.append(i.getName())
        if i.getName() == trigger.group(2):
            i.use(bot, player)
            player.items.remove(i)
            found = True
            break
    if not found:
        item_list = player.item_list()
        if item_list is None:
            bot.say(trigger.nick + ' has no items.')
        else:
            bot.say(trigger.nick + ' does not have a ' + trigger.group(2)
                    + '. Possibilities are ' + ', '.join(player.item_list())
                    + '.')

