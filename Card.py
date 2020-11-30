
import arcade

# Face down image
FACE_DOWN_IMAGE = "src/red_back.png"

class Card(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1, weight=0):
        """ Card constructor """

        # Attributes for suit and value
        self.suit = suit
        self.value = value
        self.weight = weight

        # Image to use for the sprite when face up
        self.image_file_name = f"src/{self.value}{self.suit}.png"
        
        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale, False)

    def face_down(self):
        """ Turn card face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        """ Turn card face-up """
        self.texture = arcade.load_texture(self.image_file_name)
        
        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Is this card face down? """
        return not self.is_face_up

class Button(arcade.Sprite):
    """ Button sprite """

    def __init__(self, buttonImage1, buttonImage2):
        """ Button constructor """
        
        self.buttonImage1 = buttonImage1
        self.buttonImage2 = buttonImage2
        
        # Image to use for the sprite when face up
        self.image_file_name1 = f"src/{buttonImage1}"
        self.image_file_name2 = f"src/{buttonImage2}"

        self.isPressed = False

        super().__init__(self.image_file_name1, 1, False)

    def buttonPress(self):
        """ press button """
        self.texture = arcade.load_texture(self.image_file_name2)
        self.isPressed = True

    def buttonRelease(self):
        """ release button """
        self.texture = arcade.load_texture(self.image_file_name1)
        self.isPressed = False

    @property
    def isButtonPressed(self):
        return self.isPressed