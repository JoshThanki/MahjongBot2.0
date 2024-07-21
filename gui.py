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

fontPath = "Assets//Fonts//"
font1 = "HanYiShuHunTiJian-1.ttf"
font2 = "JinXiHaoLong-1.otf"
font3 = "汉仪尚巍手书W.ttf"
font4 = "NotoSansKR.ttf"
font5 = "FZHT.ttf"


DARKGREY = (53, 47, 61)
YELLOW = (179, 168, 114)

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
                
        res.append([[Tile(sprite_sheet_pos=convertIndex(tile)) for tile in meld] for meld in playerMelds])
    
    # print([[[str(tile) for tile in melds] for melds in player] for player in res])

    return res


def convertHand(hand):
    res = []

    for tile, count in enumerate(hand):
        while count > 0:
            res.append(Tile(sprite_sheet_pos=convertIndex(tile), scale=HANDTILESCALE, handTile=True))

    return res  

def convertOrderedPool(pool):
    return [[Tile(sprite_sheet_pos=convertIndex(tile)) for tile in playerpool] for playerpool in pool]


class GUI:
    #orderedMelds =  [i = player]  (lowestTile, meldType = (0 - chi, 1 - pon, 2 - kan, 3 - closed kan))

    def __init__(self, hand = [1 if i in [i for i in range(13)] else 0 for i in range(34)], 
                    orderedMelds = [[(1,0)],[(1,0), (2,0)],[(1,0), (2,0), (3,0), (3,0)],[(1,0), (2,0), (3,0)]],
                    orderedPool = [[1,2,3],[4,5,6],[7,7,6],[]],
                    playerWinds = [0,1,2,3], 
                    wallTiles = 70



        
                    ):

        # Load the background image
        self.screen = screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        pygame.display.set_caption("Mahjong with Pygame")
        background_image_path = os.path.join(ASSETS_PATH, BACKGROUND_IMAGE_NAME)
        self.background_image = load_image(background_image_path)
    

        self.handTiles = convertHand(hand)

        self.melds = convertOrderedMelds(orderedMelds)

        self.pool = convertOrderedPool(orderedPool) 


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

            for i, discards in self.pool:
                
                discardSurface = create_discard_surface()
                for tileNo, tile in enumerate(discards):
                    x = SPRITE_FRAME_WIDTH * SPRITE_SCALE * (tileNo % 6)
                    y = SPRITE_FRAME_HEIGHT * SPRITE_SCALE * (tileNo // 6)

                    discardSurface.blit(tile.image, (x,y))

                if i == 0:
                    playerOffset = (512 - 108, 512 + 108)
                    newSurface = pygame.transform.rotate(surface, 0)
                elif i == 1:
                    playerOffset = (512 + 108 , 512 + 108)
                    newSurface = pygame.transform.rotate(surface, 90)
                elif i == 2:
                    playerOffset = (512 + 108, 512 - 108)
                    newSurface = pygame.transform.rotate(surface, 180)
                else:
                    playerOffset = (512 - 108, 512 - 108)
                    newSurface = pygame.transform.rotate(surface, 270)
                
                self.screen.blit(newSurface, (playerOffset))


            size = 216
            center_surface = create_center_surface()
            pos = (1024//2) - (size//2)

            self.screen.blit(center_surface, (pos,pos))

            # Update the display
            pygame.display.flip()

        pygame.quit()
        sys.exit()

def loadFont(path, size = 30):
    font = pygame.font.Font(fontPath + path, size)

    return font

def loadText(text, font, color = (0, 0, 0)):
    text_surface = font.render(text, True, color)

    return text_surface


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

def create_discard_surface(rows = 4):
    width = SPRITE_FRAME_WIDTH * SPRITE_SCALE * 6 
    height = SPRITE_FRAME_HEIGHT * SPRITE_SCALE * rows

    discard_surface =  pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
    discard_surface.set_alpha(120)

    return discard_surface


DARKGREY = (60, 60, 60)
BLACK = (0, 0, 0)
YELLOW = (204, 153, 0)
LIGHT_BLUE = (32, 178, 170)
WHITE = (255, 255, 255)


def create_center_surface(winds=["E", "S", "W", "N"], points=[25000, 25000, 25000, 25000], roundWind="East", round="10", wallTiles=50, dealer=0, playerTurn=1, riichi=[False, True, False, True]):
    size = 216
    radius = 20
    inward_offset = 10  # Define inward offset

    # Calculate the center of the main rectangle
    main_rect_center_x = size // 2
    main_rect_center_y = size // 2

    # Load fonts (replace None with actual font paths if necessary)
    windFont = loadFont(font2, 37)
    totalRoundFont = loadFont(font2, 22)
    numFont = loadFont(font4, 20)

    # Create a new surface with alpha transparency
    center_surface = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()

    # Fill the entire surface with dark grey
    center_surface.fill((50, 50, 50))  # DARKGREY is (50, 50, 50)
    
    # Draw a rounded rectangle
    pygame.draw.rect(center_surface, (50, 50, 50), (0, 0, size, size), border_radius=radius)
    
    # Define the corner positions in anticlockwise order starting from bottom-left
    corners = [(radius, size - radius), (size - radius, size - radius), (size - radius, radius), (radius, radius)]
    
    # Define rotation angles for each wind direction
    wind_angles = {
        "E": 0,
        "S": 90,
        "W": 180,
        "N": 270  # Corrected rotation for North
    }
    
    # Define edge midpoint positions for the points
    midpoints = [
        ((radius + (size - radius)) // 2, size - radius),  # Midpoint between East and South (bottom edge)
        (size - radius, ((radius + (size - radius)) // 2)),  # Midpoint between South and West (right edge)
        ((radius + (size - radius)) // 2, radius),  # Midpoint between West and North (top edge)
        (radius, ((radius + (size - radius)) // 2))  # Midpoint between North and East (left edge)
    ]
    
    # Colors
    wind_color = (255, 255, 255)  # Default wind color (White)
    active_wind_color = (255, 0, 0)  # Color for the active player's wind (Red)
    highlight_color = (255, 255, 0)  # Color for the highlight rectangle (Yellow)

    # Load the Riichi stick image
    riichi_image = pygame.image.load("Assets//RiichiStick.png").convert_alpha()

    # Scale down the Riichi stick image
    scale_factor = 0.4  # Adjust this value to scale the image down
    original_width, original_height = riichi_image.get_size()
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    riichi_image = pygame.transform.scale(riichi_image, (new_width, new_height))
    # Draw the winds and points at corners and midpoints


    for i, (wind, point) in enumerate(zip(winds, points)):
        # Determine the wind color
        color = active_wind_color if i == dealer else wind_color

        # Get the corner position for winds (do not move winds inward)
        corner_x, corner_y = corners[i]

        # Draw the wind text
        wind_surface = windFont.render(wind, True, color)
        wind_surface = pygame.transform.rotate(wind_surface, wind_angles[wind])
        wind_rect = wind_surface.get_rect(center=(corner_x, corner_y))
        center_surface.blit(wind_surface, wind_rect)

        # Get the midpoint position for points
        midpoint_x, midpoint_y = midpoints[i]

        # Move the midpoint position slightly inward towards the center
        direction_x = main_rect_center_x - midpoint_x
        direction_y = main_rect_center_y - midpoint_y

        nudge = 0.37

        magnitude = (direction_x**2 + direction_y**2)**nudge
        direction_x /= magnitude
        direction_y /= magnitude

        midpoint_x += direction_x * inward_offset
        midpoint_y += direction_y * inward_offset

        # Draw the points text
        point_surface = numFont.render(str(point), True, (255, 255, 0))  # YELLOW is (255, 255, 0)
        # Rotate the point text to face the same direction as the corresponding wind
        rotated_point_surface = pygame.transform.rotate(point_surface, wind_angles[wind])
        point_rect = rotated_point_surface.get_rect(center=(midpoint_x, midpoint_y))
        
        center_surface.blit(rotated_point_surface, point_rect)

        # Draw yellow rectangle for the active player's turn
        if i == playerTurn:
            # Adjust the width and height for a long stick appearance
            rect_width, rect_height = 60, 7  # Longer width, shorter height for a stick-like appearance

            # Create a surface for the trapezium with transparency
            trapeziumSurface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)

            # Define the points for the trapezium (trapezoid) with the larger side on top
            top_width = rect_width  # Width of the top side
            bottom_width = rect_width * 0.6  # Width of the bottom side, 60% of the top width
            top_left = (0, 0)
            top_right = (top_width, 0)
            bottom_left = ((top_width - bottom_width) / 2, rect_height)
            bottom_right = (top_width - (top_width - bottom_width) / 2, rect_height)

            # Draw the trapezium on the surface
            pygame.draw.polygon(trapeziumSurface, highlight_color, [top_left, top_right, bottom_right, bottom_left])

            # Rotate the trapezium surface if needed
            rotated_trapeziumSurface = pygame.transform.rotate(trapeziumSurface, wind_angles[wind])

            # Calculate the trapezium's position
            rect_x = midpoint_x - rotated_trapeziumSurface.get_width() // 2
            rect_y = midpoint_y - rotated_trapeziumSurface.get_height() // 2  # Center the trapezium with the text

            direction_x = main_rect_center_x - midpoint_x
            direction_y = main_rect_center_y - midpoint_y

            nudge = 0.4

            # Adjust the direction to nudge the trapezium inward
            magnitude = (direction_x**2 + direction_y**2)**nudge
            direction_x /= magnitude
            direction_y /= magnitude

            rect_x -= direction_x * inward_offset
            rect_y -= direction_y * inward_offset

            # Blit the rotated trapezium onto the main surface
            center_surface.blit(rotated_trapeziumSurface, (rect_x, rect_y))

        # Blit the Riichi stick if the player has declared Riichi
        if riichi[i]:
            # Rotate the Riichi stick image
            rotated_riichi_image = pygame.transform.rotate(
                riichi_image, wind_angles[wind]
            )

            # Calculate the Riichi stick's position
            riichi_x = midpoint_x - rotated_riichi_image.get_width() // 2
            riichi_y = midpoint_y - rotated_riichi_image.get_height() // 2

            direction_x = main_rect_center_x - midpoint_x
            direction_y = main_rect_center_y - midpoint_y

            nudge = 0.34 # Positive value to nudge outward

            # Adjust the direction to nudge the Riichi stick outward
            magnitude = (direction_x**2 + direction_y**2) ** nudge
            direction_x /= magnitude
            direction_y /= magnitude

            # Move the Riichi stick outward instead of inward
            riichi_x -= direction_x * inward_offset
            riichi_y -= direction_y * inward_offset

            # Blit the rotated Riichi stick onto the main surface
            center_surface.blit(rotated_riichi_image, (riichi_x, riichi_y))

    # Draw the current turn in the center using a standard font for consistency
    totalRound = roundWind + " " + round

    totalRound_surface = totalRoundFont.render(totalRound, True, (173, 216, 230))  # LIGHT_BLUE is (173, 216, 230)
    totalRound_rect = totalRound_surface.get_rect(center=(size // 2, size // 2 - 10))  # Move up by 10 pixels
    center_surface.blit(totalRound_surface, totalRound_rect)

    # Draw the wallTiles text below the totalRound text
    wallTiles_surface = totalRoundFont.render(f"x{wallTiles}", True, (173, 216, 230))  # Same font and color
    wallTiles_rect = wallTiles_surface.get_rect(center=(size // 2, size // 2 + 25))  # Positioned below the totalRound text
    center_surface.blit(wallTiles_surface, wallTiles_rect)

    return center_surface

        

    
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


class Tile:
    def __init__(self, position = (0,0), handTile = False, scale = SPRITE_SCALE, sprite_sheet_pos = (0,0), colourKey = SPRITE_COLOR_KEY):

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