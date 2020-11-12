
"""
 * Durak (fool) popular card game
  
 * @author Ivan komlev <ivankomlev@gmail.com>
 * @github https://github.com/Ivan-Komlev/Durak
 * @copyright Copyright (C) 2020. All Rights Reserved
 * @license GNU/GPL Version 2 or later - http://www.gnu.org/licenses/gpl-2.0.html
 
"""

import random, pygame
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600

BGCOLOR = ( 0, 55, 0)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Durak')

    while True:
        runGame()
        #showGameOverScreen()

def runGame():
    DISPLAYSURF.fill(BGCOLOR)

    carImg = pygame.image.load('src/2C.png')
    DISPLAYSURF.blit(carImg, (0,0))

    pygame.display.update()
    FPSCLOCK.tick(FPS)
    

if __name__ == '__main__':
    main()