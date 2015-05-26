#Tutorial created for Pyweek August 2010

# A. Starting a GalaxyMageRedux Server #

To quickly get a server running start the script run\_server.py in the main GalaxyMageRedux/pyweek folder. It will prompt you for a port number, but you can leave it blank to use the default port (54321). It will bind to localhost and attempt to bind your internet address. It will print that IP so that you may share it with your friends. Be sure to note the port number you use so that you can open it if you are behind a NAT or in your software firewalls.

# B. Playing GalaxyMageRedux #

## 1. Connecting to a Server ##

You play Galaxy Mage by starting the run\_client.py script. It will ask for your Username (can be anything, at least 4 chars long), the server (localhost if you are playing by yourself, or the address of a remote server), and the port number of the server you are
connecting to. If you connect you'll be taken to the Server Lobby.

## 2. Server Lobby ##

Here you can see the users connected to the server, the games on the server, and the chat for the server. To begin a game either click on one of the games that are joinable or click on Create a new Game.

## 3. Creating a Game ##

You will be asked for a name for a game and you can choose one of the available scenarios. You can find out how to add or create new scenarios below in "C. Modding GalaxyMageRedux."

## 4. Game Lobby ##

Before an actual game starts, you will sit in the game lobby. You can chat to other players as you wait for everyone to connect. You can choose a different scenario and you can choose which of the available teams you want to be on.
If you want to play by yourself or if you are tired of waiting for players you can click Start Game, which will load the scenario and fill empty team slots by computer bots.

## 5. Game Play ##

Once in game you will see the battle field which has tiles, Units, and other entities such as walls. The Units have flags next to them denoting which team they belong to.
The controls and information takes up the bottom portion of the screen. If you click on a unit, his stats will show up at the bottom and a menu of available abilities will pop up next to him.
Choose the abilities or move each unit on your team until you are satisfied. Then you can click end game. The next connected player or an AI bot will make their decisions. And the game will play on until the scenario game over condition is met.
You can also leave before the game is over. If the game ends, the game over screen will show up. If you or another player disconnects you will be taken back to the Server Lobby.

# C. Modding GalaxyMageRedux #

Galaxy Mage Redux is composed of scenarios, abilities, images, and units. There is a main folder for each of these in /data/ Also, scenario specific abilities, images and units are found in `/data/scenarios/<scenario>/`

## 1. Images ##
The images folder holds all the sprites and tile images. Sprites may be PNG or Animated GIFs. Tiles should be PNG. The images can be any size, just be sure to update your scenario with the proper size of the tiles (which should all be the same size.

## 2. Abilities and Units ##
Abilities and Units are python scripts that create new classes based on BaseAbility and BaseUnit (whose classes are in the lib/mod\_base.py).

## 3. Scenarios ##
In the Scenarios folder are more folders which act like game packages. These folders hold abilities, images, and units folders just like the main data folder. All the files in the main abilities, images, and units folders can be used by the scenarios. But the data from each scenario are not shared.

Scenarios also have four main scripts: ai.py, config.py, scenario.py, and map.py.

The ai.py controls how the bot units will play in this scenario.

The map.py sets up the geometric shape, the tile types/placement, and the location of other map entities like walls or bridges.

The config.py script controls the specific variables name (the name of the scenario as it will show up in scenario selection), num\_players (the number of players or bots needed to play the game), and  teams (the names of the different teams).

The scenario.py is the main script that sets up the game. It holds all the units for the scenario and their attributes. It determines the winning screen and the messages needed to inform the player of the scenarios story context.

That's the overview of what you need to do to create your own Scenario or Mod. When you have one completed you can compress the folder of your scenario and share it. To install a scenario package just extract it under the data/scenario folder and enjoy!