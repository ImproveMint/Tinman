from player import Player
from random import randrange
from constants import Action

class randomplayer(Player):
    def get_action(self, gamestate):
        num_actions = 3
        action = randrange(num_actions)
        betsize = 0

        if action == Action.CALL:
            betsize = Player.max_committed - self.committed

            if Player.min_raise > self.get_stack():
                betsize = self.get_stack()

        elif action == Action.BET_RAISE:
            if Player.min_raise > self.get_stack():
                betsize = self.get_stack()
            else:
                betsize = randrange(Player.min_raise, self.get_stack())

        return action, betsize
