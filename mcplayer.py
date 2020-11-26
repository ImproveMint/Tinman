'''
Initial Primitive version of player that implements some sort of MC play
'''

import eval_c
from player import Player
from randomplayer import randomplayer
from constants import Action, Street
from random import randrange
from deck import Deck
from card import Card

class mcplayer(Player):

    deck = Deck()

    def get_action(self, gamestate):

        num_actions = 3
        betsize = 0

        wins = self.__run_sim(100, gamestate)

        if wins > 50 and wins <= 65:
            action = Action.CALL

            betsize = Player.street_max_committed - self.street_committed

            if betsize > self.get_stack():
                betsize = self.get_stack()

        elif wins > 65:
            action = Action.BET_RAISE

            if self.min_bet() >= self.get_stack():
                betsize = self.get_stack()
            else:
                betsize = randrange(self.min_bet(), self.get_stack())

        else:
            action = Action.CHECK_FOLD

        #If the betsize is 0 then it's actually a check
        if betsize == 0:
            action = Action.CHECK_FOLD

        assert(betsize > 0 or action == Action.CHECK_FOLD)

        return action, betsize

    def __run_sim(self, sims, gamestate):
        won = 0
        ranks = []

        street = gamestate.get("street")
        board = gamestate.get("board")
        remain = gamestate.get("remain") -1

        remove_cards = []
        remove_cards.extend(self.get_hand())

        #Work around to get flop to do some bad shit
        if street == Street.PREFLOP:
            remove_cards.extend(board)
            ranks.append(self.get_hand_rank(board, Street.RIVER))
        else:
            remove_cards.extend(board[:street + 2])
            ranks.append(self.get_hand_rank(board, street))

        for sim in range(sims):
            best_rank = 7463 #One worse than worst ranking hand
            winner = 0 # resets winning player to this player (index 0)

            #Remove this player's hand and the board cards from simulated deck
            mcplayer.deck.shuffle()
            mcplayer.deck.remove(remove_cards)

            #Give remaining players in hand a random hand
            for _ in range(1, remain):
                if street == Street.FLOP:
                    ranks.append(eval_c.evaluate5(board[:street +2], mcplayer.deck.draw(2)))

                elif street == Street.TURN:
                    ranks.append(eval_c.evaluate6(board[:street +2], mcplayer.deck.draw(2)))

                elif street == Street.RIVER or street == Street.PREFLOP:
                    ranks.append(eval_c.evaluate7(board, mcplayer.deck.draw(2)))

            #lowest ranked hand is the better hand
            #note that split pot hands are considered wins
            best_rank = min(rank for rank in ranks)

            # This player won
            if ranks[0] == best_rank:
                won+=1

            for _ in range(1, remain):
                ranks.pop()

        return won
