# run with
# python -m unittest rpg-unittests
# you may have to modify your path to point to your sopel instance

import sys
print(sys.path)
sys.path.append('../sopel')

import unittest

from rpg import *


class BotStub():
    def __init__(self):
        self.said = ""
    def say(self, st):
        self.said = self.said + st

    

class TestItems(unittest.TestCase):

    def test_newItem(self):
        p = Potion()
        self.assertEqual('potion', p.getName())

class TestBrick(unittest.TestCase):

    def test_newFeatures(self):
        p = mage_class()
        p.load()
        b = LooseBrick()
        bot = BotStub()
        b.item = Potion()

        b.getEffect(bot, p)
        self.assertEqual(bot.said, "mage gets a potion.")
  

if __name__ == '__main__':
    unittest.main()

