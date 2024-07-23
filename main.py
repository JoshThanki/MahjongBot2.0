import threading
import time
from game import Game
from gui import GUI

# Define a function to run the game loop
def run_game(game):
    print("Starting game loop")
    start = time.time()
    game.main()
    print("Finished game loop")
    end = time.time()
    print(f"Time: {end - start}")

# Define a function to run the GUI loop
def run_gui(gui):
    print("Starting GUI loop")
    gui.main()
    print("Finished GUI loop")

print("START")

# Initialize the game
game = Game()
print("Finish Init game")

# Initialize the GUI with game data
gui = GUI(game.gameData)

# Create threads for the game and GUI
game_thread = threading.Thread(target=run_game, args=(game,))
gui_thread = threading.Thread(target=run_gui, args=(gui,))

# Start the threads
game_thread.start()
gui_thread.start()

print("Threads started")