from player import Player
from random import randrange
from constants import Action

class randomplayer(Player):
    def get_action(self, gamestate):
        num_actions = 3
        action = randrange(num_actions)
        betsize = 0

        if action == Action.CALL:
            betsize = Player.street_max_committed - self.street_committed

            if betsize > self.get_stack():
                betsize = self.get_stack()

        elif action == Action.BET_RAISE:
            if self.min_bet() >= self.get_stack():
                betsize = self.get_stack()
            else:
                betsize = randrange(self.min_bet(), self.get_stack())

        if betsize == 0:
            action = Action.CHECK_FOLD

        assert(betsize > 0 or action == Action.CHECK_FOLD)

        return action, betsize
