import time
import threading
from game import Player


class Powerup:
    def __init__(self):
        self.player = Player(speed=5)
        self.running = True

    def run(self):
        while self.running:
            self.update()
            self.render()
            time.sleep(0.016)  

    def update(self):
        self.player.move()

    def render(self):
        pass

    def apply_speed(self, duration):
        def powerup_thread():
            self.player.speed = True
            self.player.speed *= 2
            for i in range(duration):
                print(f"Powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            self.player.speed /= 2
            self.player.speed = False
            print("Powerup ended")

        threading.Thread(target=powerup_thread).start()

    game = Powerup()

    game.apply_speed(duration=30)
    print(f"Speed after powerup: {game.player.speed}")

    game.run()
    pass




class Powerup:
    def __init__(self):
        pass
    def render(self):
        pass

    def apply_ghost(self, duration):
        def powerup_thread():
            self.player.ghost = True
            # self.player.collision = False
            for i in range(duration):
                print(f"Powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            # self.player.collision = True
            self.player.ghost = False
            print("Ghost powerup ended")

        threading.Thread(target=powerup_thread).start()

    game = Powerup()

    game.apply_ghost(duration=10)
    print(f"Gohst time: {game.player.speed}")

    game.run()

    pass

class Powerup:
    def __init__(self):
        pass
    def render(self):
        pass

    def apply_shield(self, duration):
        def powerup_thread():
            self.player.shield = True
            # self.player.tagged = False
            for i in range(duration):
                print(f"Powerup active: {duration - i} seconds remaining")
                time.sleep(1)
            # self.player.tagged = True
            self.player.shield = False
            print("Shield powerup ended")

        threading.Thread(target=powerup_thread).start()

    game = Powerup()

    game.apply_shield(duration=30)
    print(f"Shield time: {game.player.speed}")

    game.run()
    pass






