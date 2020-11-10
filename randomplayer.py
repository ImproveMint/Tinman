from player import Player
from random import randrange

class randomplayer(Player):
    def get_action(self, gamestate):
        betsize = 0
        num_actions = 3
        action = randrange(num_actions)

        if action == 1:
            betsize = Player.max_committed - self.committed

            if Player.min_raise > self.get_stack():
                betsize = self.get_stack()

        elif action == 2:
            if Player.min_raise > self.get_stack():
                betsize = self.get_stack()
            else:
                betsize = randrange(Player.min_raise, self.get_stack())

        return action, betsize
