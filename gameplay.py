import Table
import random

class gameplay():
    def __init__(self):
        
        #self.cardDeck=[]

        self.trumpSuit=random.choice(Table.CARD_SUITS)

    def newGame(self):

        self.trumpSuit=random.choice(Table.CARD_SUITS)



