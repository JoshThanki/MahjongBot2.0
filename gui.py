import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1800, 1000
BACKGROUND_COLOR = (255, 255, 255)  # White background
ASSETS_PATH = 'Assets'  # Directory where your image is stored
IMAGE_NAME = 'table.jpg'  # Image filename



# Create a resizable display window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Mahjong")

# Load the background image
try:
    background_image_path = os.path.join(ASSETS_PATH, IMAGE_NAME)
    background_image = pygame.image.load(background_image_path)
except pygame.error as e:
    print(f"Unable to load image: {e}")
    pygame.quit()
    sys.exit()

# Function to scale the image to fit the window size
def get_scaled_image(image, window_size):
    return pygame.transform.scale(image, window_size)

scaled_background = get_scaled_image(background_image, (WIDTH, HEIGHT))

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the main loop
        elif event.type == pygame.VIDEORESIZE:
            # Update window size and rescale the background image
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            scaled_background = get_scaled_image(background_image, (WIDTH, HEIGHT))

    # Draw the background image
    screen.blit(scaled_background, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
