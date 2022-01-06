import random
import random
import arcade
import arcade.gui

import time

from Card import Card
from Card import Button




# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Durak - Card Game"

#Display pages
PAGE_GAME = 1
PAGE_HELP = 2

# Constants for sizing
CARD_SCALE = 0.6

# How big are the cards?
CARD_WIDTH = 100 * CARD_SCALE
CARD_HEIGHT = 153 * CARD_SCALE

# How big is the mat we'll place the card on?
MAT_PERCENT_OVERSIZE = 1.10
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

# How much space do we leave as a gap between the mats?
# Done as a percent of the mat size.
VERTICAL_MARGIN_PERCENT = 0.10
HORIZONTAL_MARGIN_PERCENT = 0.10

# The Y of the bottom row (2 piles)
BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the left side
START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# The Y of the top row (4 piles)
TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# The X of where to start putting things on the right side
END_X = SCREEN_WIDTH - MAT_WIDTH / 2 - MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

# The X of the middle row (game table)
MIDDLE_X = SCREEN_WIDTH / 2 + MAT_WIDTH / 2 # - MAT_WIDTH - MAT_WIDTH * VERTICAL_MARGIN_PERCENT

# The Y of the middle row
MIDDLE_Y = SCREEN_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT
Y_SPACING = MAT_HEIGHT + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# Card constants
global CARD_VALUES, CARD_SUITS
CARD_VALUES = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
#CARD_VALUES = ["J", "Q", "K", "A"]
CARD_SUITS = ["C", "H", "S", "D"] #["Clubs", "Hearts", "Spades", "Diamonds"]

# If we fan out cards stacked on each other, how far apart to fan them?
CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3

# Constants that represent "what pile is what" for the game

BOTTOM_FACE_DOWN_PILE = 1
BOTTOM_FACE_DONE = 2
BOTTOM_FACE_UP_PILE = 0

class Table(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        
        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = None

        arcade.set_background_color(arcade.color.AMAZON)

        # List of cards we are dragging with the mouse
        self.held_cards = None

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = None

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list = None

        # Create a list of lists, each holds a pile of cards.
        self.piles = None

        self.buttons = None
        self.Help_buttons = arcade.SpriteList()

        #self.ui_manager = UIManager()

        self.Attack = 0 # 0 is the enemy, but should be definde by smallest trump card
        self.Turn = 0 # 0 is the enemy, but should be definde by smallest trump card

        self.trumpSuit=""

        self.gameInProgress = False

        self.page = PAGE_GAME

        #buttons


        button = Button('resume.png', 'resume_pressed.png')
        button.position = MIDDLE_X - 38, BOTTOM_Y - 20
        button.task="Resume"
        self.Help_buttons.append(button);


        f = open("rules.txt", "r")
        self.Rules = f.read()

        self.smallestTrumpCards = [1000000,1000000] #this to determine who moves first. 1000000 is imposibly high weight

        self.victory = -1

        self.clock = time.time()

        print (self.clock)


    def setupPiles(self):

        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()
        self.piles = []

        # Create the mats for the trump card
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, MIDDLE_Y #This is the face up deck pile (Trump)
        pile.enemy=False
        pile.myCard=False
        pile.game=False
        self.pile_mat_list.append(pile)
        self.piles.append([])

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, MIDDLE_Y #This is the face back deck pile (Bank)
        pile.enemy=False
        pile.myCard=False
        pile.game=False
        self.pile_mat_list.append(pile)
        self.piles.append([])

        # Create the mats for the done piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = END_X - MAT_WIDTH, MIDDLE_Y #This is the face back deck pile (Bank)
        pile.enemy=False
        pile.myCard=False
        pile.game=False
        self.pile_mat_list.append(pile)
        self.piles.append([])

    def pullTrumpCard(self):
        
        card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
        card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
        card.face_up()
        self.trumpSuit = card.suit

        #cards=[]
        #cards.append(card)

        self.piles[BOTTOM_FACE_UP_PILE].append(card)
    
    def findEmptyPile(self,isEnemy,myCard):

        for pile_no in range(len(self.pile_mat_list)):
            if ((isEnemy and self.pile_mat_list[pile_no].enemy) or (myCard and self.pile_mat_list[pile_no].myCard)) and len(self.piles[pile_no])==0:
                return pile_no

        return -1

    def pullCards(self,isEnemy,myCard):

        #check mats, add if needed
        count=0
        
        for pile in self.pile_mat_list:
            if (isEnemy and pile.enemy) or (myCard and pile.myCard):
                count += 1

        if count == 0:
            numberOfMatsOnHand = 6
            for i in range(6):
                pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
                pile.position = MIDDLE_X - (numberOfMatsOnHand * X_SPACING / 2 ) + i * X_SPACING, TOP_Y if isEnemy else BOTTOM_Y
                pile.enemy=isEnemy
                pile.myCard=myCard
                pile.game=False
                self.pile_mat_list.append(pile)

                cards=[]
                self.piles.append(cards)

        #min number of cards 6
        #get the ammount of cards already in the pile

        count=0

        for pile_no in range(len(self.piles)):
            if ((isEnemy and self.pile_mat_list[pile_no].enemy) or (myCard and self.pile_mat_list[pile_no].myCard)) and len(self.piles[pile_no])!=0:
                count += 1

        for i in range(6):
            if count < 6:
                card = None
                if len(self.piles[BOTTOM_FACE_DOWN_PILE])>0:
                    card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                elif len(self.piles[BOTTOM_FACE_UP_PILE])>0:
                    card = self.piles[BOTTOM_FACE_UP_PILE].pop()
                else:
                    break

                if card.suit == self.trumpSuit:
                    index_ = 0 if isEnemy else 1
                    if card.weight < self.smallestTrumpCards[index_]:
                        self.smallestTrumpCards[index_] = card.weight

                if card is not None:

                    pile_no = self.findEmptyPile(isEnemy,myCard)
                    if pile_no!=-1:
                        pile=self.pile_mat_list[pile_no]
                    
                        card.position = pile.position

                        if isEnemy:
                            card.face_down()
                        else:
                            card.face_up()

                        self.piles[pile_no].append(card)

                        count+=1

    def isAllAttacksCompleted(self):
        numberOfattacks = 0
        unfinishedAttackes=0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game and len(self.piles[pile_no])==2:
                numberOfattacks += 1
            elif self.pile_mat_list[pile_no].game and len(self.piles[pile_no])==1:
                unfinishedAttackes += 1

        return numberOfattacks > 0 and unfinishedAttackes == 0

    def get_numberOfCompletedAttacks(self):
        numberOfattacks = 0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game and len(self.piles[pile_no])==2:
                numberOfattacks += 1

        return numberOfattacks

    def get_numberOfCardsOnTheTable(self):
        numberOfattacks = 0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game:
                numberOfattacks += len(self.piles[pile_no])
                
        return numberOfattacks

    def get_numberOfAttackMats(self):
        numberOfMats= 0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game:
                numberOfMats += 1

        return numberOfMats

    def takeCards(self,isEnemy,myCard):

        count = 0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.game:
                count += len(self.piles[pile_no])

        if count>0:
            numberOfCardsOnHand = 0
            numberOfMatsOnHand = 0
            for pile_no in range(len(self.pile_mat_list)):
                pile=self.pile_mat_list[pile_no]
                if (isEnemy and pile.enemy) or (myCard and pile.myCard):
                    numberOfMatsOnHand += 1
                    numberOfCardsOnHand += len(self.piles[pile_no])

            numberOfMatsToAdd = numberOfCardsOnHand + count - numberOfMatsOnHand

            for i in range(numberOfMatsToAdd):
                pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
                pile.position = numberOfMatsOnHand * X_SPACING + START_X + i * X_SPACING, TOP_Y if isEnemy else BOTTOM_Y
                pile.enemy=isEnemy
                pile.myCard=myCard
                pile.game=False
                self.pile_mat_list.append(pile)
                cards=[]
                self.piles.append(cards)


            #move cards
            for pile_no in range(len(self.pile_mat_list)):
                pile=self.pile_mat_list[pile_no]
                if pile.game:
                    cards=self.piles[pile_no]
                    for card_index_ in range(len(cards)):
                        card_index=len(cards)-card_index_-1
                        
                        pile_no_to = self.findEmptyPile(isEnemy, myCard)
                        if pile_no_to != -1:
                            cards[card_index].position = self.pile_mat_list[pile_no_to].position

                            if isEnemy:
                                cards[card_index].face_down()
                            else:
                                cards[card_index].face_up()

                            self.move_card_to_new_pile(cards[card_index], pile_no_to)

            self.centerPlayerCards(isEnemy,myCard)

            self.newTurn(False)
                
    def centerPlayerCards(self,isEnemy,myCard):

        numberOfMatsOnHand = 0
        for pile_no in range(len(self.pile_mat_list)):
            pile=self.pile_mat_list[pile_no]
            if (isEnemy and pile.enemy) or (myCard and pile.myCard):
                numberOfMatsOnHand += 1
                
        #reposition mats - center allign them
        i=0

        custom_X_SPACING = X_SPACING
        if numberOfMatsOnHand > 10:
            custom_X_SPACING = custom_X_SPACING - (numberOfMatsOnHand - 10) * 2.5

        for pile_no in range(len(self.pile_mat_list)):
            pile=self.pile_mat_list[pile_no]
            if (isEnemy and pile.enemy) or (myCard and pile.myCard):
                pile.position = MIDDLE_X - (numberOfMatsOnHand * custom_X_SPACING / 2 ) + i * custom_X_SPACING, TOP_Y if isEnemy else BOTTOM_Y
                
                cards = self.piles[pile_no]

                p=0
                for card in cards:
                    card.position = MIDDLE_X - (numberOfMatsOnHand * custom_X_SPACING / 2 ) + i * custom_X_SPACING, TOP_Y if isEnemy else BOTTOM_Y
                    p += 1

                i+=1


    def orientButtons(self):

        cardsOnTheTable = self.get_numberOfCardsOnTheTable()

        if self.Attack == 0:
            if cardsOnTheTable>0:
                self.buttons[1].position = MIDDLE_X - 38, MIDDLE_Y - 150
            else:
                self.buttons[1].position = -1000, -1000


            if self.isAllAttacksCompleted():
                self.buttons[0].position = MIDDLE_X - 38, MIDDLE_Y + 150
            else:
                self.buttons[0].position = -1000, -1000

        else:
            if cardsOnTheTable>0:
                self.buttons[1].position = MIDDLE_X - 38, MIDDLE_Y + 150
            else:
                self.buttons[1].position = -1000, -1000

            if self.isAllAttacksCompleted():
                self.buttons[0].position = MIDDLE_X - 38, MIDDLE_Y - 150
            else:
                self.buttons[0].position = -1000, -1000
            
                    
    def newMove(self):
        
        self.do_draw()
        if self.checkForVictory():
            return

        numberOfCompleteAttacks = self.get_numberOfCompletedAttacks()
        numberOfMats = self.get_numberOfAttackMats()
        
        if numberOfMats == numberOfCompleteAttacks:
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = MIDDLE_X + (numberOfMats - 1) * X_SPACING, MIDDLE_Y 
            pile.enemy=False
            pile.myCard=False
            pile.game=True
            self.pile_mat_list.append(pile)
            cards=[]
            self.piles.append(cards)

        count = 0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.game:
                count +=1
        
        #reposition mats - center align them
        i=0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.game:
                pile.position = MIDDLE_X - (count * X_SPACING / 2 ) + i * X_SPACING, MIDDLE_Y 
                
                cards = self.piles[pile_no]

                p=0
                for card_no in range(len(cards)):
                    cardOffset = p * 10
                    cards[card_no].position = MIDDLE_X - (count * X_SPACING / 2 ) + i * X_SPACING + cardOffset, MIDDLE_Y - cardOffset 
                    print ("newMove:Card Value: " + cards[card_no].value)
                    print ("newMove:Card Sute: " + cards[card_no].suit)
                    
                    
                    p += 1

                i+=1

        self.orientButtons()

        self.do_draw()

        

    def checkIfCardCanBeAdded(self,dropped_card):

        #check if similar 
        validMove = False
        countCards = 0

        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game:
                cards = self.piles[pile_no]

                for card in cards:
                    countCards += 1
                    if dropped_card.value == card.value:
                        validMove = True
                        break

        if countCards > 0 and not validMove:
            return False #improper move
        else:
            return True #proper move

    def getCardToBeBitten(self):

        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game:
                cards = self.piles[pile_no]
                if len(cards) == 1:
                    return cards[0]

        return None;

    def moveTheEnemyCard(self,smallestCard,attack = True):
        #get move pile
        pile = None
        count = 0
        for pile_index in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_index].game:
                if attack and len(self.piles[pile_index]) == 0:
                    pile = self.pile_mat_list[pile_index]
                    break
                elif not attack and len(self.piles[pile_index]) == 1:
                    pile = self.pile_mat_list[pile_index]
                    count = 1
                    break
                
        if pile != None:
            # Move cards to proper position
            cardOffset = count * 10
            smallestCard.position = pile.center_x + cardOffset, \
                                                pile.center_y - cardOffset

            self.move_card_to_new_pile(smallestCard, pile_index)

    def getPileIndex2Move(self,attack = True):
        for pile_index in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_index].game:
                if attack and len(self.piles[pile_index]) == 0:
                    return pile_index
                    break
                elif not attack and len(self.piles[pile_index]) == 1:
                    return pile_index
                    break


    def ComputerMove(self):

        if self.Attack == 0 and self.Turn == 0:
            #Computer is Attacking

            #Find the smallest card that is legal to play
            smallestCard = None

            for pile_no in range(len(self.pile_mat_list)):
                if self.pile_mat_list[pile_no].enemy:
                    cards = self.piles[pile_no]

                    for card in cards:
                        if self.checkIfCardCanBeAdded(card):
                            if smallestCard == None:
                                smallestCard = card
                            else:
                                if card.weight < smallestCard.weight:
                                    smallestCard = card;

            if smallestCard != None:
                                    
                smallestCard.face_up()
                self.moveTheEnemyCard(smallestCard, True)
                self.do_draw()

                self.Turn +=1
                if self.Turn==2:
                    self.Turn=0

                self.newMove()
            else:
                #Computer is pressing "Done" button
                self.newTurn()

        elif self.Turn == 0:
            #Computer Defending
            
            #Find the smallest card that is legal to play
            smallestCard = None

            top_card = self.getCardToBeBitten()

            if top_card != None:
                for pile_no in range(len(self.pile_mat_list)):
                    if self.pile_mat_list[pile_no].enemy:
                        cards = self.piles[pile_no]

                        for card in cards:
                            if card.suit == top_card.suit:
                                if card.weight > top_card.weight:
                                    if smallestCard == None:
                                        smallestCard = card
                                    else:
                                        if card.weight < smallestCard.weight:
                                            smallestCard = card
                                    

                            elif card.suit == self.trumpSuit:
                                if card.weight > top_card.weight:
                                    if smallestCard == None:
                                        smallestCard = card
                                    else:
                                        if card.weight < smallestCard.weight:
                                            smallestCard = card

            if top_card != None and smallestCard != None:
                                    

                pile_index= self.getPileIndex2Move(False)
                #self.moveTheEnemyCard(smallestCard, False)

                for pile in self.piles:
                    if smallestCard in pile:
                        pile.remove(smallestCard)
                        break
                
                self.piles[pile_index].append(smallestCard)

                cardOffset =  10
                smallestCard.position = self.pile_mat_list[pile_index].center_x + cardOffset, self.pile_mat_list[pile_index].center_y - cardOffset
                smallestCard.face_up()

                self.do_draw()

                self.Turn +=1
                if self.Turn==2:
                    self.Turn=0

                self.newMove()
            else:
                #Computer is pressing "Take" button
                self.takeCards(True, False) # this is in revers - the defender may take cards


    def newTurn(self,changeTheTurn=True):

        #move cards to the done pile
        pile=self.pile_mat_list[BOTTOM_FACE_DONE]

        for pile_no_ in range(len(self.pile_mat_list)):
            pile_no=len(self.pile_mat_list)-pile_no_-1
            
            if self.pile_mat_list[pile_no].game:

                cards=self.piles[pile_no]
                for card_index_ in range(len(cards)):
                    card_index=len(cards)-card_index_-1
                    #cards[card_index].position = pile.position

                    l=len(self.piles[BOTTOM_FACE_DONE])
                    xOffset=l*2
                    yOffset=l*2-10
                    cards[card_index].position = END_X - xOffset - 57, MIDDLE_Y + yOffset #bank cards
                           

                    cards[card_index].face_down()
                    self.move_card_to_new_pile(cards[card_index], BOTTOM_FACE_DONE)

                #del self.piles[pile_no]
                #del self.pile_mat_list[pile_no]
    
        if self.Attack == 0:
            self.pullCards(True, False)
            self.pullCards(False, True)
        else:
            self.pullCards(False, True)
            self.pullCards(True, False)

        if changeTheTurn:
            self.Attack +=1
            if self.Attack==2:
                self.Attack=0

        self.Turn = self.Attack

        self.orientButtons()
        
        self.checkForVictory()

        self.ComputerMove()
    
    def checkForVictory(self):

        enemyCards = 0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.enemy:
                enemyCards += len(self.piles[pile_no])

        playerCards = 0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.myCard:
                playerCards += len(self.piles[pile_no])

        print ("enemyCards:", enemyCards)
        print ("playerCards:", playerCards)

        if enemyCards == 0 and playerCards!=0:
            print ("Computer won!")

            self.gameInProgress = False
            self.victory = 0

            button = Button('again.png', 'again_pressed.png')
            button.position = MIDDLE_X - 38, MIDDLE_Y - 120
            button.task="Start Over"
            self.buttons[0]=button;
            self.buttons[1].remove_from_sprite_lists()
            

            return True
        elif playerCards == 0 and enemyCards != 0:
            print ("You won!")

            self.gameInProgress = False
            self.victory = 1

            button = Button('again.png', 'again_pressed.png')
            button.position = MIDDLE_X - 38, MIDDLE_Y - 120
            button.task="Start Over"
            self.buttons[0]=button;
            self.buttons[1].remove_from_sprite_lists()

            return True

    def setWhoPlaysFirst():
        self.trumpSuit

    def mixTheDeck(self):

        self.card_list = arcade.SpriteList()

        for card_suit in CARD_SUITS:
            v=6
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                #card.position = START_X + xOffset, MIDDLE_Y - yOffset #bank cards
                card.weight = v 

                self.card_list.append(card)
                v+=1

        #Shuffle the cards

        Shuffle_card_list = arcade.SpriteList()
        taken = [];
        while len(Shuffle_card_list) < len(self.card_list):
            random_pos = random.randrange(len(self.card_list))
            if not(random_pos in taken):
                taken.append(random_pos)
                Shuffle_card_list.append(self.card_list[random_pos])

        self.card_list = Shuffle_card_list
        #Shuffle_card_list.clear()
        
        # Put all the cards in the bottom face-down pile
        xOffset=0
        yOffset=0

        i=0
        for card in self.card_list:
            card.position = START_X + xOffset, MIDDLE_Y - yOffset #bank cards
            
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

            if i==0:
                self.pullTrumpCard()

            xOffset += 2
            yOffset += 2
            i += 1

        #Set Values
        for card in self.card_list:
            if card.suit == self.trumpSuit:
                card.weight = card.weight * 10

        #Pull cards

        self.pullCards(True, False)
        self.pullCards(False, True)

        

        #Set who moves first
        if self.smallestTrumpCards[0]!=1000000 and self.smallestTrumpCards[1]!=1000000:
            #if both have trump cards
            if self.smallestTrumpCards[0] < self.smallestTrumpCards[1]:
                self.Attack = 0
            else:
                self.Attack = 1
        else:
            #if only one has trump card
            if self.smallestTrumpCards[0]!=1000000:
                self.Attack = 0
            else:
                self.Attack = 1

    def setup(self):
        self.victory = -1
        """ Set up the game here. Call this function to restart the game. """

        self.gameInProgress = True
        
        self.setupPiles()


        # --- Create, shuffle, and deal the cards

        # Sprite list with all the cards, no matter what pile they are in.
        
        self.buttons = arcade.SpriteList()


        #buttons
        button = Button('done.png', 'done_pressed.png')
        button.position = MIDDLE_X - 38, MIDDLE_Y - 120
        button.task="Done"
        self.buttons.append(button);

        button = Button('take.png', 'take_pressed.png')
        button.position = MIDDLE_X - 38, MIDDLE_Y - 190
        button.task="Take Cards"
        self.buttons.append(button);

        button = Button('help.png', 'help_pressed.png')
        button.position = MIDDLE_X - 38, MIDDLE_Y + 100
        button.task="Help"
        self.buttons.append(button);

        # Create every card, will be nice to add some animation
        
        self.Attack = -1
        while (self.Attack == -1):
            self.smallestTrumpCards = [1000000,1000000]
            self.mixTheDeck()
            print("self.Attack:",self.Attack)

        self.Turn = self.Attack

        self.newMove()

        #""" Set up this view. """
        #self.ui_manager.purge_ui_elements()

        y_slot = self.height - 40
        left_column_x = self.width // 2
        right_column_x = 3 * self.width // 4

        self.newTurn(False)

        arcade.draw_text(SCREEN_TITLE, MIDDLE_X - 40, MIDDLE_Y + 200, arcade.color.WHITE, 14)


    def do_draw(self):
        """ Render the screen. """
        
        arcade.start_render()

        if self.page == PAGE_GAME:
            self.buttons.draw()
            self.pile_mat_list.draw()
            self.card_list.draw()
            #self.ui_manager._ui_elements.draw()
            arcade.draw_text(SCREEN_TITLE, SCREEN_WIDTH / 2 - 100, MIDDLE_Y + 200, arcade.color.WHITE, 16, width=200,align="center")

            if self.victory == 0:
                arcade.draw_text("Computer won!", SCREEN_WIDTH / 2 - 150, TOP_Y - 100, arcade.color.WHITE, 24, width=300,align="center")
            elif self.victory == 1:
                arcade.draw_text("You won!", SCREEN_WIDTH / 2 - 150, BOTTOM_Y + 80, arcade.color.WHITE, 24, width=300,align="center")

        elif self.page == PAGE_HELP:
            #arcade.draw_text("Rules", SCREEN_WIDTH / 2 - 100 , TOP_Y, arcade.color.WHITE, 14, width=200,align="center")
            arcade.draw_text(self.Rules, SCREEN_WIDTH / 2 - 500 , BOTTOM_Y +10, arcade.color.WHITE, 14, width=1000,align="left")
            self.Help_buttons.draw()
    
    def on_draw(self):
        self.do_draw()

        if self.clock + 1 < time.time():
            self.clock = time.time()

            if self.Turn == 0 and self.gameInProgress:
                self.ComputerMove()
                self.do_draw()


    def pull_to_top(self, card):
        """ Pull card to top of rendering order (last to render, looks on-top) """
        # Find the index of the card
        index = self.card_list.index(card)
        # Loop and pull all the other cards down towards the zero end
        for i in range(index, len(self.card_list) - 1):
            self.card_list[i] = self.card_list[i + 1]
        # Put this card at the right-side/top/size of list
        self.card_list[len(self.card_list) - 1] = card

    def on_key_press(self, symbol: int, modifiers: int):
        """ User presses key """
        if symbol == arcade.key.R:
            # Restart
            self.setup()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of buttons we've clicked on
        buttons = arcade.get_sprites_at_point((x, y), self.buttons)
        if len(buttons) > 0:
            button = buttons[-1]
            button.buttonPress()

        HelpButtons = arcade.get_sprites_at_point((x, y), self.Help_buttons)
        if len(HelpButtons) > 0:
            button = HelpButtons[-1]
            button.buttonPress()

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)
            
            # Are we clicking on the bottom deck, to flip three cards?
            if pile_index == BOTTOM_FACE_DOWN_PILE or pile_index == BOTTOM_FACE_DONE  or pile_index == BOTTOM_FACE_UP_PILE:
                #cannot touch this cards
                return False
                #self.Turn

            elif self.pile_mat_list[pile_index].game:
                #cannot touch this cards
                return False
            elif self.Turn == 0 and self.pile_mat_list[pile_index].myCard:
                #cannot touch this cards
                return False
            elif self.Turn == 1 and self.pile_mat_list[pile_index].enemy:
                #cannot touch this cards
                return False
            else:
                # All other cases, grab the face-up card we are clicking on
                self.held_cards = [primary_card]
                # Save the position
                self.held_cards_original_position = [self.held_cards[0].position]
                # Put on top in drawing order
                self.pull_to_top(self.held_cards[0])

                # Is this a stack of cards? If so, grab the other cards too
                card_index = self.piles[pile_index].index(primary_card)
                for i in range(card_index + 1, len(self.piles[pile_index])):
                    card = self.piles[pile_index][i]
                    self.held_cards.append(card)
                    self.held_cards_original_position.append(card.position)
                    self.pull_to_top(card)
                    
    def remove_card_from_pile(self, card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if card in pile:
                pile.remove(card)
                break

    def get_pile_for_card(self, card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if card in pile:
                return index

    def move_card_to_new_pile(self, card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(card)
        self.piles[pile_index].append(card)
        print ("Card: " + card.value)

    
        
        
    def checkTheMove(self,pile,pile_index):

        #is the pile complete
        if len(self.piles[pile_index]) == 2:
            return True

        # Are you attacking?
        if self.Attack == self.Turn and len(self.piles[pile_index]) == 0:
            

            dropped_card = self.held_cards[0]

            if not self.checkIfCardCanBeAdded(dropped_card):
                return True #improper move
            
            for i, dropped_card in enumerate(self.held_cards):
                # Move cards to proper position
                cardOffset =i * 10
                #dropped_card.position = pile.center_x + cardOffset, \
                                                #pile.center_y - CARD_VERTICAL_OFFSET * i - cardOffset

                self.move_card_to_new_pile(dropped_card, pile_index)
                self.do_draw()

        elif self.Attack != self.Turn and len(self.piles[pile_index]) == 1: # Are you defending?


            # Move cards to proper position
            top_card = self.piles[pile_index][-1]
            for i, dropped_card in enumerate(self.held_cards):
                dropped_card.position = top_card.center_x, \
                                               top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)

            if dropped_card.suit != top_card.suit and dropped_card.suit != self.trumpSuit:
                return True #improper move

            if dropped_card.weight <= top_card.weight:
                return True

            self.move_card_to_new_pile(dropped_card, pile_index)


            if self.get_numberOfAttackMats() < 6:
                #add game mat
                self.newMove()
            
            if self.get_numberOfCompletedAttacks() == 6:
                self.newTurn()
                return False

        else:
            return True

        self.Turn +=1
        if self.Turn==2:
            self.Turn=0

        
        #self.orientButtons()

        #self.ComputerMove()

        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        # Release all buttons
        
        buttons = arcade.get_sprites_at_point((x, y), self.buttons)
        if len(buttons) > 0:
            button = buttons[-1]
            if button.isButtonPressed:
                
                if button.task == "Take Cards":
                    self.takeCards(self.Attack == 1, self.Attack == 0) # this is in revers - the defender may take cards
                elif button.task == "Done":
                    if self.isAllAttacksCompleted():
                        self.newTurn()
                elif button.task == "Start Over":
                    self.setup()
                elif button.task == "Help":
                    self.page = PAGE_HELP
                elif button.task == "Resume":
                    self.page = PAGE_HELP

        HelpButtons = arcade.get_sprites_at_point((x, y), self.Help_buttons)
        if len(HelpButtons) > 0:
            button = HelpButtons[-1]
            if button.isButtonPressed:
                if button.task == "Resume":
                    self.page = PAGE_GAME
        
        for button in self.buttons:
            button.buttonRelease()

        # If we don't have any cards, who cares
        if len(self.held_cards) == 0:
            return

        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_cards[0], pile):

            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came  from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif self.pile_mat_list[pile_index].game:
                reset_position = self.checkTheMove(pile,pile_index)
                
        if reset_position:
            # Where-ever we were dropped, it wasn't valid. Reset the each card's position
            # to its original spot.
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]

        # We are no longer holding cards
        self.held_cards = []

        if not reset_position:
            self.newMove()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


