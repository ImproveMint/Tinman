from random import choice
from card import Card
from deck import Deck
from evaluator import Evaluator
from agent import Agent
from agent import Action
from time import sleep
from enum import IntEnum
import logging, sys

class Street(IntEnum):
    #At this time I'm not really using this. The next_street method just resets everything but I
    #don't think it's important the the program know which street we're on.
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

class Game:
    street = Street.PREFLOP #This is garbage for now.

    def __init__(self, agent1, agent2, BIG_BLIND = 100, SMALL_BLIND = 50, NUM_BB = 100, logging_level=logging.INFO):
        logging.basicConfig(stream=sys.stderr, level=logging_level)

        self.agents = [agent1, agent2]

        self.button = choice([0, 1]) #randomly chooses player that is first to act IE who is button and small blind
        self.deck = Deck()

        #Will update to C evaluator in the future. Seems like C is 10x faster than pure python implementation.
        self.evaluator = Evaluator()
        self.board = []
        self.hands = []

        self.BIG_BLIND = BIG_BLIND
        self.SMALL_BLIND = SMALL_BLIND
        self.NUM_BB = NUM_BB

        self.min_raise = BIG_BLIND
        self.pot = 0
        self.bet_size = 0
        self.last_bet = 0

        self.player_folded = False
        self.player_allin = False
        self.street_ended = False
        self.num_street_actions = 0

    def start(self):
        self.deck.shuffle()
        self.board.append(self.deck.draw(5))
        self.hands.append(self.deck.draw(2))
        self.hands.append(self.deck.draw(2))

        #Preflop
        self.post_blinds()
        self.agents[0].dealHand(self.hands[0])
        self.agents[1].dealHand(self.hands[1])
        self.agents[0].print_player()
        self.agents[1].print_player()
        self.betting_round()
        self.button = (self.button+1)%2 #After preflop the first to act changes. Also after this hand this agent will be first to act next hand so no need to change it again.

        #Flop
        if not self.player_folded:
            logging.debug("-------------Flop-------------")
            Card.print_pretty_flop(self.board[0])
            self.betting_round()

        #Turn
        if not self.player_folded:
            logging.debug("-------------Turn-------------")
            Card.print_pretty_turn(self.board[0])
            self.betting_round()

        #River
        if not self.player_folded:
            logging.debug("-------------River-------------")
            Card.print_pretty_river(self.board[0])
            self.betting_round()

        #Showdown
        if not self.player_folded:
            logging.debug("-------------Showdown-------------")
            self.showdown()

    def betting_round(self):
        #every street brings a new betting round and so I think all we need to know is who goes first
        #Have to find a way for the program to run when a player goes all in, the other player has to decide to call or fold.

        while not self.player_folded and not self.player_allin and not self.street_ended:
            self.num_street_actions+= 1
            action, raise_size = self.agents[self.button].get_action(self.bet_size)
            self.process_action(action, raise_size)
            self.button = (self.button+1)%2

        self.next_street()
        self.street_ended = False;

    def process_action(self, action, raise_size = 0):
        logging.debug("Player :")
        #logging.debug("Commited:", self.agents[self.button].committed)
        #logging.debug("Bet_size:", self.bet_size)
        #logging.debug(self.street_actions)
        difference = self.bet_size - self.agents[self.button].committed

        if action == Action.CALLCHECK:
            if difference == 0:
                logging.debug("Checks")
                if self.num_street_actions > 1:
                    self.next_street()
            else:
                logging.debug("Calls $" + str(difference/100))
                if self.num_street_actions > 1:
                    self.pot+=difference
                    self.next_street()

        elif action == Action.FOLDCHECK:
            if difference == 0:
                logging.debug("Checks")
                if self.num_street_actions > 1:
                    self.next_street()
            else:
                logging.debug("Folds")
                self.process_fold()

        elif action == Action.RAISE:
            logging.debug("Raises $" + str(raise_size/100))
            self.pot+=raise_size
            self.min_raise = raise_size - self.last_bet
            self.last_bet = raise_size
            self.bet_size = self.agents[self.button].committed + self.agents[self.button].bet(raise_size)
        else:
            logging.debug("Something is wrong at process_action")

    def process_fold(self):
        self.bet_size = 0
        self.player_folded = True
        self.agents[(self.button+1)%2].add_chips(self.pot)

        self.next_street()

    def next_street(self):
        for agent in self.agents:
            agent.committed = 0

        self.num_street_actions = 0
        self.bet_size = 0
        self.last_bet = 0
        self.min_raise = self.BIG_BLIND
        self.street_ended = True
        #Don't think we'll need this
        #self.street = Street((int(self.street) + 1) % 4)

    def post_blinds(self):
        self.pot += self.agents[self.button].post_small(self.SMALL_BLIND)
        logging.debug("Player " + str(self.button) +  " posted small blind.")
        self.pot += self.agents[(self.button+1)%2].post_big(self.BIG_BLIND)
        logging.debug("Player " + str((self.button+1)%2) + " posted big blind.")
        self.bet_size = self.BIG_BLIND
        self.last_bet = self.BIG_BLIND

    def showdown(self):
        handRank0 = self.evaluator.evaluate(self.board[0], self.hands[0])
        handRank1 = self.evaluator.evaluate(self.board[0], self.hands[1])

        #Smaller handRank = better hand
        #Agent0 (seat1) won the pot
        if handRank0 < handRank1:
            logging.debug(self.agents[0].player_name + " wins a pot of $" + str(self.pot/100))
            self.agents[0].add_chips(self.pot)

        #Agent1 (seat2) won the pot
        elif handRank1 < handRank0:
            logging.debug(self.agents[1].player_name + " wins a pot of $ " + str(self.pot/100))
            self.agents[1].add_chips(self.pot)

        #Split pot. I realize there's a rounding error here - I don't care at this time
        elif handRank0 == handRank1:
            logging.debug("Splitpot")
            self.agents[0].add_chips(self.pot/2)
            self.agents[1].add_chips(self.pot/2)

        else:
            logging.debug("Something went wrong at Showdown.")

        self.pot = 0

if __name__ == "__main__":
    game = Game(Agent(), Agent())
    game.start()
