# IRC RPG

This is a simple, but extensible, role-playing game that is text-based, and
designed to be used in an IRC chat.

## Design goals

1. Start command, allowing users to create an nxm sized map.
2. In true RPG form there are character classes to start, there should be:
    1. Mage - magic caster. Low HP, but big damage
    2. Fighter - meat shield. High HP, good damage
    3. Healer - heals the team. Mid HP, low damage, special ability to heal
    4. Thief - Low HP, but high probabilty to dodge, special stealing ability
3. Users then have 30s or a minute to register to play
4. Users then choose a class. After 30s they are assigned a random one.
5. Fighting is turn-based. Initiative is rolled on encounter. 'sleeping' users
   will do random attacks after 1 minute (configurable? work-friendly mode)
6. Map is a grid. Bot will show exits N/E/S/W.
7. Map is random. Has guaranteed path from start to finish
8. Map visualizer is a must, even if it only shows rooms that are within 
   3 adjacent blocks (7x7 grid shown). This is more a limitation of what 
   IRC is friently with.
9. Memory: Mosters are spawned when level is created. If you leave a room and 
   come back immediately, the room shouldn't be swarmed with monsters.
   Spawning more monsters during play is probably fair game.
10. Permadeath? Rogue-like?
11. Rooms can have features, like fountains or waterfalls... or traps.

Obviously a lot of this is inspired from Nethack. I don't expect the game to
become that complicated.

## How to read the map:

The map is an important part of the system.
Currently this is in design phase, so is potentially could change

Example map:

    +--------+
    |?s.?    |
    |  ..    |
    |  ?.    |
    |   ..?  |
    |    .   |
    |    .?  |
    |    e   |
    +--------+

Dictionary:
- ? - unvisited room that you know exists
- s - start
- e - end
- . - visited room
- -, | and + - the frame to make it pretty

## Commands

- .startrpg - start the RPG. Users now have to register for the game
- .register - register for the game. You will be prompted for which class
  you would like to be.
- .move [north/east/south/west] - move to the next room. If you are in combat,
  enemies get an opportunity attack on the team. You have a random chance of
  escaping based on the number of opponents in the room
- .attack - attack using whatever weapon you are holding.
- .special - special attack, class-based.
- .interact [item] - interact with an item you're holding, or that is in the
  room. This could have positive or negative effects!
- .inventory - show your inventory.
- .item [itemname] - use an item. If the item needs a target/destination, you
   will be prompted.
- .bail - quit the team. This also happens if you leave the chat room. Game
  ends if all players die or bail.
