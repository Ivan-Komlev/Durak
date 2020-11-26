import random
import random
import arcade
import arcade.gui
from arcade.gui import UIManager

from Card import Card
from Card import Button

# Screen title and size
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Durak - Card Game"

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
MIDDLE_X = SCREEN_WIDTH / 2 # - MAT_WIDTH - MAT_WIDTH * VERTICAL_MARGIN_PERCENT

# The Y of the middle row
MIDDLE_Y = SCREEN_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# How far apart each pile goes
X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT
Y_SPACING = MAT_HEIGHT + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

# Card constants
global CARD_VALUES, CARD_SUITS
CARD_VALUES = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
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

        self.ui_manager = UIManager()

        self.Attack = 0 # 0 is the enemy, but should be definde by smallest trump card
        self.Turn = 0 # 0 is the enemy, but should be definde by smallest trump card

        self.trumpSuit=""

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

        cards=[]
        cards.append(card)

        self.piles.append(cards)
    
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
            for i in range(6):
                pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
                pile.position = START_X + i * X_SPACING, TOP_Y if isEnemy else BOTTOM_Y
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
                print ("l=",len(self.piles[pile_no]))
                count += 1

        print("Cards in piles: ",count)

        for i in range(6):
            if count < 6:
                card = None
                if len(self.piles[BOTTOM_FACE_DOWN_PILE])>0:
                    card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                elif len(self.piles[BOTTOM_FACE_UP_PILE])>0:
                    card = self.piles[BOTTOM_FACE_UP_PILE].pop()
                else:
                    break

                if card is not None:

                    pile_no = self.findEmptyPile(isEnemy,myCard)
                    if pile_no!=-1:
                        pile=self.pile_mat_list[pile_no]
                    
                        card.position = pile.position

                        if isEnemy:
                            card.face_up()#card.face_down()
                        else:
                            card.face_up()

                        self.piles[pile_no].append(card)

                        count+=1


    def get_numberOfattacks(self):
        numberOfattacks = 0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game:
                numberOfattacks += 1

        return numberOfattacks

    def get_numberOfCompletedAttacks(self):
        numberOfattacks = 0
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].game and len(self.piles[pile_no])==2:
                numberOfattacks += 1

        return numberOfattacks

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
                            self.move_card_to_new_pile(cards[card_index], pile_no_to)

            self.newTurn(False)
                
            
                    
    def newMove(self):
        numberOfattacks = self.get_numberOfattacks()
        
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = MIDDLE_X + (numberOfattacks - 1) * X_SPACING, MIDDLE_Y 
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
        
        i=0
        for pile_no in range(len(self.pile_mat_list)):
            pile = self.pile_mat_list[pile_no]
            if pile.game:
                pile.position = MIDDLE_X - (count * X_SPACING / 2 ) + i * X_SPACING, MIDDLE_Y 
                
                cards = self.piles[pile_no]

                p=0
                for card in cards:
                    cardOffset = p * 6
                    card.position = MIDDLE_X - (count * X_SPACING / 2 ) + i * X_SPACING + cardOffset, MIDDLE_Y - cardOffset 
                    p += 1

                i+=1

        
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
    

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        
        self.setupPiles()


        # --- Create, shuffle, and deal the cards

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()
        self.buttons = arcade.SpriteList()

        
        # Create every card, will be nice to add some animation
        
        for card_suit in CARD_SUITS:
            v=6
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                #card.position = START_X + xOffset, MIDDLE_Y - yOffset #bank cards
                card.value = v 

                self.card_list.append(card)
                v+=1

        #Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list[pos1], self.card_list[pos2] = self.card_list[pos2], self.card_list[pos1]
        
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
                card.value = card.value * 10

        #Pull cards

        self.pullCards(True, False)
        self.pullCards(False, True)

        self.newMove()

        """ Set up this view. """
        self.ui_manager.purge_ui_elements()

        y_slot = self.height - 40
        left_column_x = self.width // 2
        right_column_x = 3 * self.width // 4

        # left side elements
        self.ui_manager.add_ui_element(arcade.gui.UILabel(
            SCREEN_TITLE,
            center_x=MIDDLE_X - 40,
            center_y=MIDDLE_Y + 200,
        ))


        #buttons
        button = Button('take.png', 'take_pressed.png')
        button.position = MIDDLE_X - 38, MIDDLE_Y - 120
        button.task="Take Cards"
        self.buttons.append(button);

        button = Button('button.png', 'button.png')
        button.position = MIDDLE_X - 38, MIDDLE_Y + 100
        button.task="Help"
        self.buttons.append(button);


    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        arcade.start_render()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

        self.ui_manager._ui_elements.draw()

        self.buttons.draw()

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

        
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

    def checkTheMove(self,pile,pile_index):

        #is the pile complete
        if len(self.piles[pile_index]) == 2:
            return True

        # Are there already cards there?
        if self.Attack != self.Turn and len(self.piles[pile_index]) == 1:
            # Move cards to proper position
            top_card = self.piles[pile_index][-1]
            for i, dropped_card in enumerate(self.held_cards):
                dropped_card.position = top_card.center_x, \
                                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)

            if dropped_card.suit != top_card.suit and dropped_card.suit != self.trumpSuit:
                return True #improper move

            if dropped_card.value < top_card.value:
                return True

            self.move_card_to_new_pile(dropped_card, pile_index)

            if self.get_numberOfattacks() < 6:
                #add game mat
                self.newMove()
            
            if self.get_numberOfCompletedAttacks() == 6:
                self.newTurn()
                return False


        elif self.Attack == self.Turn and len(self.piles[pile_index]) == 0:
            # Are there no cards in the middle play pile?
            for i, dropped_card in enumerate(self.held_cards):
            # Move cards to proper position
                cardOffset =i * 6
                dropped_card.position = pile.center_x + cardOffset, \
                                                pile.center_y - CARD_VERTICAL_OFFSET * i - cardOffset

                self.move_card_to_new_pile(dropped_card, pile_index)
        else:
            return True

        self.Turn +=1
        if self.Turn==2:
            self.Turn=0

        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        # Release all buttons
        
        buttons = arcade.get_sprites_at_point((x, y), self.buttons)
        if len(buttons) > 0:
            button = buttons[-1]
            print(button.task)
            self.takeCards(self.Attack == 1, self.Attack == 0) # this is in revers - the defender may take cards

        
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

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy


