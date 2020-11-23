from player import Player
from randomplayer import randomplayer
from constants import Action, Street
from random import randrange
import eval_c


from deck import Deck
from card import Card

class mcplayer(Player):

    deck = Deck()

    def get_action(self, gamestate):
        #Need some black box simulator for MC to generate search

        #I'm realizing based on how slow it is to run 2500 games (~2min)
        #That running thousands of sims for each decision that mcplayer makes
        #might be prohibitive.

        #An alternative idea for a first MC agent would be to make bets that are
        #correlated to how likely the agent is to win at the river against any 2
        #random cards.
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

        '''
        example - run 1000 sims of checking
        -run 1000 sims of folding
        -run 1000 sims of betting 1/2 pot
        -run 1000 sims of betting 1/3 pot
        -run 1000 sims of betting 3/4 pot
        -run 1000 sims of betting pot
        -run 1000 sims of all in
        -run 1000 sims of min raising
        -run 1000 sims of 3x raising

        something like that,

        TTC - are all actions after the action taken random? I think so
        Even though the agent should technically only receive a reward for
        winning there needs to be a way to evaluate the actions and so I
        guess it should be by EV for that hand?
        '''

    '''
    trivial Monte Carlo, give other players 2 random cards and see who wins on river
    we ignore all other information included future betting
    '''
    def __run_sim(self, sims, gamestate):

        won = 0
        ranks = []

        street = gamestate.get("street")
        board = gamestate.get("board")
        remain = gamestate.get("remain") -1

        remove_cards = []
        remove_cards.extend(board)
        remove_cards.extend(self.get_hand())

        ranks.append(self.get_hand_rank(board, street))

        for sim in range(sims):
            best_rank = 7463
            winner = 0 # resets winning player to this player (index 0)
            #Remove this player's hand and board cards from deck
            mcplayer.deck.shuffle()
            mcplayer.deck.remove(remove_cards)

            #Give remaining players in hand a random hand
            for _ in range(1, remain):
                if street == Street.FLOP:
                    ranks.append(eval_c.evaluate5(board, mcplayer.deck.draw(2)))

                elif street == Street.TURN:
                    ranks.append(eval_c.evaluate6(board, mcplayer.deck.draw(2)))

                else:
                    ranks.append(eval_c.evaluate7(board, mcplayer.deck.draw(2)))

            #lowest ranked hand is the better hand
            #One thing to note is that split pot hands are considered wins
            best_rank = min(rank for rank in ranks)

            # This player won
            if ranks[0] == best_rank:
                won+=1

            for _ in range(1, remain):
                ranks.pop()

        return won
