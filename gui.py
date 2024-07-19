import pygame
import sys
import os

# Constants
WIDTH, HEIGHT = 1024, 1024  # Adjusted window height for better display
ASSETS_PATH = 'Assets'  # Directory where your images are stored
BACKGROUND_IMAGE_NAME = 'table.jpg'  # Background image filename
SPRITESHEET_IMAGE_NAME = 'hand_ui.png'  # Spritesheet filename
SPRITE_FRAME_WIDTH = 80  # Width of a single sprite frame in the sheet
SPRITE_FRAME_HEIGHT = 129  # Height of a single sprite frame in the sheet
SPRITE_SCALE = 0.45  # Scale factor for the sprite
HANDTILESCALE = 0.6
SPRITE_COLOR_KEY = (0, 0, 0)  # Color key for transparency in the sprite sheet
SPRITE_SPACING = 10  # Spacing between sprites

# Initialize Pygame
pygame.init()

class Spritesheet:
    def __init__(self, filename, scale, colour_key, width, height):
        filepath = os.path.join(ASSETS_PATH, filename)
        self.spriteSheet = pygame.image.load(filepath).convert_alpha()
        self.scale = scale
        self.colour_key = colour_key
        self.width = width
        self.height = height

    def get_image(self, frame, flip_horizontal=False):
        """
        Retrieve a sprite image from the sprite sheet using row and column indices.

        :param frame: Tuple (row, column) indicating the sprite's position in the sprite sheet.
        :param flip_horizontal: Boolean indicating whether to flip the image horizontally.
        :return: The scaled and possibly flipped sprite image.
        """
        # Calculate the x and y positions on the sprite sheet
        row, col = frame
        x = col * self.width
        y = row * self.height

        # Create a new surface and blit the sprite onto it
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.spriteSheet, (0, 0), (x, y, self.width, self.height))

        # Scale and optionally flip the image
        image = pygame.transform.scale(image, (int(self.width * self.scale), int(self.height * self.scale)))
        image = pygame.transform.flip(image, flip_horizontal, False)

        # Set the color key for transparency
        image.set_colorkey(self.colour_key)

        return image
    

def load_image(image_path):
    try:
        return pygame.image.load(image_path).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        pygame.quit()
        sys.exit()


def convertIndex(index):
    suit = index//9
    number = index % 9

    suitConv = {
        0: 1, #mans
        1 : 2, #pins
        2 : 0, #sou
    }

    if suit < 3:
        return ((suitConv[suit], number + 1))
    else:
        return((3, number))
    
def convertOrderedMelds(orderedMelds):
    res = []

    for melds in orderedMelds:

        playerMelds = []

        for meld in melds:
            if meld[1] == 0:
                playerMelds.append([i for i in range(meld[0], meld[0]+3)])
            elif meld[1] == 1:
                playerMelds.append([meld[0]] * 3)
            elif meld[1] == 2:
                playerMelds.append([meld[0]] * 4)
            elif meld[1] == 3:
                playerMelds.append([meld[0], 34, 34, meld[0]]) #34 blank tile
            else:
                print("Unknown Meld")
                exit()
                
        res.append([[Tile(sprite_sheet_pos=convertIndex(tile), handTile=False) for tile in meld] for meld in playerMelds])
    
    print([[[str(tile) for tile in melds] for melds in player] for player in res])

    return res



    

class GUI:
    #orderedMelds =  [i = player]  (lowestTile, meldType = (0 - chi, 1 - pon, 2 - kan, 3 - closed kan))

    def __init__(self, hand = [1 if i in [i for i in range(13)] else 0 for i in range(34)], orderedMelds = [[(1,0)],[(1,0), (2,0)],[(1,0), (2,0), (3,0), (3,0)],[(1,0), (2,0), (3,0)]], playerWinds = [0,1,2,3], wallTiles = 70):

        # Load the background image
        self.screen = screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        pygame.display.set_caption("Mahjong with Pygame")
        background_image_path = os.path.join(ASSETS_PATH, BACKGROUND_IMAGE_NAME)
        self.background_image = load_image(background_image_path)

        self.handTiles = [Tile(sprite_sheet_pos=convertIndex(tile), scale=HANDTILESCALE) for tile in range(len(hand)) if hand[tile] > 0]


        print(orderedMelds)

        self.melds = convertOrderedMelds(orderedMelds)

        self.screen.blit(self.background_image, (0, 0))

    def update(self, hand, orderedMelds = [0,0,0,0], playerWinds = [0,1,2,3], wallTiles = 70):
        pass
        
        self.handTiles = [Tile(position=(50 + 20*tile, 50), sprite_sheet_pos=convertIndex(tile)) for tile in range(len(hand)) if hand[tile] > 0]


    def main(self):
            
        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Blit the background image
            
            for i, tile in enumerate(self.handTiles):
                
                totalWidth = 1024 
                lenTiles = (SPRITE_FRAME_WIDTH * HANDTILESCALE  + 5) * len(self.handTiles)
                xoffset = (totalWidth - lenTiles) // 2 
                yoffset = 925

                tile.update(self.screen, (xoffset + (SPRITE_FRAME_WIDTH * HANDTILESCALE  + 5) * i, yoffset))

            for i, player in enumerate(self.melds):

                playerWidth, playerSurface = create_player_surface(player)

                runningMeldWidth = 0
                for meld in player:
                    meldWidth, surface = create_meld_surface(meld)

                    for tileNo, tile in enumerate(meld):
                        surface.blit(tile.image, (SPRITE_FRAME_WIDTH * SPRITE_SCALE*tileNo, 0))
                    
                    playerSurface.blit(surface, (runningMeldWidth, 0))

                    runningMeldWidth += meldWidth + 10

                
                if i == 0:
                    playerOffset = (900 - playerWidth, 850)
                    newSurface = playerSurface
                elif i == 1:
                    playerOffset = (850 , 125)
                    newSurface = pygame.transform.rotate(playerSurface, 90)
                elif i == 2:
                    playerOffset = (125, 125)
                    newSurface = pygame.transform.rotate(playerSurface, 180)
                else:
                    playerOffset = (125, 900  - playerWidth)
                    newSurface = pygame.transform.rotate(playerSurface, 270)
                
            
                self.screen.blit(newSurface, (playerOffset))


            # Update the display
            pygame.display.flip()

        pygame.quit()
        sys.exit()

def create_meld_surface(meld):
    # Calculate the width of the surface based on the length of the meld
    width = SPRITE_FRAME_WIDTH * SPRITE_SCALE * len(meld)
    height = SPRITE_FRAME_HEIGHT * SPRITE_SCALE 

    meld_surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    
    meld_surface.set_alpha(150) 

    return width, meld_surface

def create_player_surface(melds):
    width = -10
    height = SPRITE_FRAME_HEIGHT * SPRITE_SCALE 
    for meld in melds:
        width+=10
        meldWidth = SPRITE_FRAME_WIDTH * SPRITE_SCALE * len(meld)
        width+=meldWidth
    
    player_surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    
    player_surface.set_alpha(150) 


    return width, player_surface


    
    
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


class Tile:
    def __init__(self, position = (0,0), handTile = True, scale = SPRITE_SCALE, sprite_sheet_pos = (0,0), colourKey = SPRITE_COLOR_KEY):

        self.x = position[0]
        self.y = position[1]
        self.width = SPRITE_FRAME_WIDTH
        self.height = SPRITE_FRAME_HEIGHT
        self.handTile = handTile
        self.sprite_sheet_pos = sprite_sheet_pos
        self.spritesheet = Spritesheet(SPRITESHEET_IMAGE_NAME, scale, colourKey, self.width, self.height)
        self.image = self.spritesheet.get_image(self.sprite_sheet_pos)

    def update(self, screen, position = None):
        if position:
            self.x = position[0]
            self.y = position[1]

        screen.blit(self.image, (self.x, self.y))

    def __str__(self):
        return (
            f"Tile(position=({self.x}, {self.y}), "
            f"sprite_sheet_pos={self.sprite_sheet_pos}, "
        )

gui = GUI()
gui.main()