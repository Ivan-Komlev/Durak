import random
import arcade
import arcade.gui
from arcade.gui import UIManager

from Card import Card

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

BOTTOM_FACE_DOWN_PILE = 0
BOTTOM_FACE_UP_PILE = 1
"""
PLAY_PILE_1 = 2
PLAY_PILE_2 = 3
PLAY_PILE_3 = 4
PLAY_PILE_4 = 5
PLAY_PILE_5 = 6
PLAY_PILE_6 = 7
PLAY_PILE_7 = 8
TOP_PILE_1 = 9
TOP_PILE_2 = 10
TOP_PILE_3 = 11
TOP_PILE_4 = 12
"""

class HelpButton(arcade.gui.UIImageButton):

    def on_click(self):
        """ Called when user lets off button """
        print("Click flat button.")
        arcade.set_background_color(arcade.color.RED)

class Table(arcade.Window):
    """ Main application class. """

    def __init__(self, theGame):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        #Game Logic
        self.theGame = theGame
        

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

        self.ui_manager = UIManager()

    def setupPiles(self):
        

        # List of cards we are dragging with the mouse
        self.held_cards = []

        # Original location of cards we are dragging with the mouse in case
        # they have to go back.
        self.held_cards_original_position = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the mats for the bottom face down and face up piles
        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X, MIDDLE_Y #This is the face back deck pile (Bank)
        pile.enemy=False
        pile.myCard=False
        pile.game=False
        self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = START_X + X_SPACING, MIDDLE_Y #This is the face up deck pile (Trump)
        pile.enemy=False
        pile.myCard=False
        pile.game=False
        self.pile_mat_list.append(pile)

        # Create the six enemy piles
        for i in range(6):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, TOP_Y
            pile.enemy=True
            pile.myCard=False
            pile.game=False
            self.pile_mat_list.append(pile)

        # Create the six "(your) cards to play" piles
        for i in range(6):
            pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = START_X + i * X_SPACING, BOTTOM_Y
            pile.enemy=False
            pile.myCard=True
            pile.game=False
            self.pile_mat_list.append(pile)

        pile = arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN)
        pile.position = MIDDLE_X, MIDDLE_Y #This is the face up deck pile (Trump)
        pile.enemy=False
        pile.myCard=False
        pile.game=True #a place holder on the table for the move
        self.pile_mat_list.append(pile)

        self.pileCount = 1 + 1 + 6 + 6 + 1

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(self.pileCount)]


    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        self.setupPiles()


        # --- Create, shuffle, and deal the cards

        # Sprite list with all the cards, no matter what pile they are in.
        self.card_list = arcade.SpriteList()

        # Create every card, will be nice to add some animation
        for card_suit in CARD_SUITS:
            v=6
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, MIDDLE_Y #bank cards
                card.value = (v * 10 if card_suit == self.theGame.trumpSuit else v) 

                self.card_list.append(card)
                v+=1
        

        #Shuffle the cards
        for pos1 in range(len(self.card_list)):
            pos2 = random.randrange(len(self.card_list))
            self.card_list[pos1], self.card_list[pos2] = self.card_list[pos2], self.card_list[pos1]

        
        # Put all the cards in the bottom face-down pile
        for card in self.card_list:
            self.piles[BOTTOM_FACE_DOWN_PILE].append(card)

        #Pull cards
        for pile_no in range(len(self.pile_mat_list)):
            if self.pile_mat_list[pile_no].enemy:
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                self.piles[pile_no].append(card)
                card.position = self.pile_mat_list[pile_no].position
            elif self.pile_mat_list[pile_no].myCard:
                card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                self.piles[pile_no].append(card)
                card.position = self.pile_mat_list[pile_no].position
                card.face_up()
            

        
        # - Pull from that pile into the middle piles, all face-down
        # Loop for each pile
        #for pile_no in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
            # Deal proper number of cards for that pile
            #for j in range(pile_no - PLAY_PILE_1 + 1):
                # Pop the card off the deck we are dealing from
                #card = self.piles[BOTTOM_FACE_DOWN_PILE].pop()
                # Put in the proper pile
                #self.piles[pile_no].append(card)
                # Move card to same position as pile we just put it in
                #card.position = self.pile_mat_list[pile_no].position
                # Put on top in draw order
                #self.pull_to_top(card)

        # Flip up the top cards
        #for i in range(PLAY_PILE_1, PLAY_PILE_7 + 1):
           #self.piles[i][-1].face_up()


        """ Set up this view. """
        self.ui_manager.purge_ui_elements()

        y_slot = self.height - 40
        left_column_x = self.width // 2
        right_column_x = 3 * self.width // 4

        # left side elements
        self.ui_manager.add_ui_element(arcade.gui.UILabel(
            SCREEN_TITLE,
            center_x=110,  #left_column_x,
            center_y=110  #y_slot,
        ))

        button_normal = arcade.load_texture('src/button.png')
        hovered_texture = arcade.load_texture('src/button.png')
        pressed_texture = arcade.load_texture('src/button.png')
        button = HelpButton(
            center_x=self.width - 80,
            center_y=y_slot,
            normal_texture=button_normal,
            hover_texture=hovered_texture,
            press_texture=pressed_texture,
            text='--help',
        )
        self.ui_manager.add_ui_element(button)


    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        arcade.start_render()

        # Draw the mats the cards go on to
        self.pile_mat_list.draw()

        # Draw the cards
        self.card_list.draw()

        self.ui_manager._ui_elements.draw()

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

        # Get list of cards we've clicked on
        cards = arcade.get_sprites_at_point((x, y), self.card_list)

        # Have we clicked on a card?
        if len(cards) > 0:

            # Might be a stack of cards, get the top one
            primary_card = cards[-1]
            # Figure out what pile the card is in
            pile_index = self.get_pile_for_card(primary_card)
            
            # Are we clicking on the bottom deck, to flip three cards?
            if pile_index == BOTTOM_FACE_DOWN_PILE:
                # Flip three cards
                for i in range(3):
                    # If we ran out of cards, stop
                    if len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                        break
                    # Get top card
                    card = self.piles[BOTTOM_FACE_DOWN_PILE][-1]
                    # Flip face up
                    card.face_up()
                    # Move card position to bottom-right face up pile
                    card.position = self.pile_mat_list[BOTTOM_FACE_UP_PILE].position
                    # Remove card from face down pile
                    self.piles[BOTTOM_FACE_DOWN_PILE].remove(card)
                    # Move card to face up list
                    self.piles[BOTTOM_FACE_UP_PILE].append(card)
                    # Put on top draw-order wise
                    self.pull_to_top(card)

            elif primary_card.is_face_down:
                # Is the card face down? In one of those middle 7 piles? Then flip up
                primary_card.face_up()
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
                    
        else:

            # Click on a mat instead of a card?
            mats = arcade.get_sprites_at_point((x, y), self.pile_mat_list)

            if len(mats) > 0:
                mat = mats[0]
                mat_index = self.pile_mat_list.index(mat)

                # Is it our turned over flip mat? and no cards on it?
                if mat_index == BOTTOM_FACE_DOWN_PILE and len(self.piles[BOTTOM_FACE_DOWN_PILE]) == 0:
                    # Flip the deck back over so we can restart
                    temp_list = self.piles[BOTTOM_FACE_UP_PILE].copy()
                    for card in reversed(temp_list):
                        card.face_down()
                        self.piles[BOTTOM_FACE_UP_PILE].remove(card)
                        self.piles[BOTTOM_FACE_DOWN_PILE].append(card)
                        card.position = self.pile_mat_list[BOTTOM_FACE_DOWN_PILE].position

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

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        """ Called when the user presses a mouse button. """

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

            #  Is it the same pile we came from?
            if pile_index == self.get_pile_for_card(self.held_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # Is it on a middle play pile?
            elif self.pile_mat_list[pile_index].game:
                # Are there already cards there?
                if len(self.piles[pile_index]) > 0:
                    # Move cards to proper position
                    top_card = self.piles[pile_index][-1]
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = top_card.center_x, \
                                                top_card.center_y - CARD_VERTICAL_OFFSET * (i + 1)
                else:
                    # Are there no cards in the middle play pile?
                    for i, dropped_card in enumerate(self.held_cards):
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, \
                                                pile.center_y - CARD_VERTICAL_OFFSET * i

                for card in self.held_cards:
                    # Cards are in the right position, but we need to move them to the right list
                    self.move_card_to_new_pile(card, pile_index)

                # Success, don't reset position of cards
                reset_position = False

            # Release on top play pile? And only one card held?
            elif TOP_PILE_1 <= pile_index <= TOP_PILE_4 and len(self.held_cards) == 1:
                # Move position of card to pile
                self.held_cards[0].position = pile.position
                # Move card to card list
                for card in self.held_cards:
                    self.move_card_to_new_pile(card, pile_index)

                reset_position = False

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