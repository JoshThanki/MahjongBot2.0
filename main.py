from game import Game
import time

game = Game()
start = time.time()
game.main()
end = time.time()
print(f"Time: {end - start}")
