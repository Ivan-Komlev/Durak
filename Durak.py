
"""
 * Durak (fool) popular card game
  
 * @author Ivan komlev <ivankomlev@gmail.com>
 * @github https://github.com/Ivan-Komlev/Durak
 * @copyright Copyright (C) 2020. All Rights Reserved
 * @license GNU/GPL Version 2 or later - http://www.gnu.org/licenses/gpl-2.0.html
 
 
 * This is the Project #3: Pick a Card Game! of Pirple.com - Python is Easy
 *  - Everyone has their favorite card game. What's yours? For this assignment, choose a card game (other than Blackjack), and turn it into a Python program.
 *  - It doesn't matter if it's a 1-player game, or a 2 player game, or more! That's totally up to you. A few requirements:
 *
 *  1. It's got to be a card game (no board games, etc)
 *  2. When the game starts up, you should ask for the players' names. And after they enter their names, your game should refer to them by name only. 
 *  ("It's John's turn" instead of "It's player 1's turn). 
 *  3. At any point during the game, someone should be able to type "--help" to be taken to a screen where they can read the rules of the game and instructions for how to play.
 *  After they're done reading, they should be able to type "--resume" to go back to the game and pick up where they left off.
 *
 * Card moving tutorial: https://arcade.academy/tutorials/card_game/index.html
 * GUI Elements: https://arcade.academy/examples/gui_elements.html
"""

import arcade

import arcade.gui
from arcade.gui import UIManager

from Table import Table
from gameplay import gameplay

if __name__ == '__main__':
    theGame = gameplay()
    theGame.newGame()

    theTable = Table(theGame)
    theTable.setup()
    

    arcade.run()

