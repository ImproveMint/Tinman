from random import choice
#from deuces import Deck, Evaluator, Card
from card import Card
from deck import Deck
from evaluator import Evaluator
from agent import Agent
from time import sleep

class Game:
    #In cents
    BIG_BLIND = 100
    SMALL_BLIND = 50

    def __init__(self, agent1, agent2):
        self.button = choice([0, 1]) #randomly chooses player that is first to act IE who is button and small blind
        self.deck = Deck()

        #Will update to C evaluator in the future. Seems like C is 10x faster than pure python implementation.
        self.evaluator = Evaluator()
        self.board = []
        self.hands = []
        self.agents = [agent1, agent2]
        self.pot = 0

    def start(self):

        self.deck.shuffle()
        self.board.append(self.deck.draw(5))
        self.hands.append(self.deck.draw(2))
        self.hands.append(self.deck.draw(2))

        #Preflop
        self.post_blinds()
        self.agents[0].dealHand(self.hands[0])
        self.agents[1].dealHand(self.hands[1])
        self.betting_round()
        self.button = (self.button+1)%2 #After preflop the first to act changes. Also after this hand this agent will be first to act next hand so no need to change it again.

        #Flop
        self.betting_round()

        #Turn
        self.betting_round()

        #River
        self.betting_round()

        #Showdown
        self.showdown()

    def betting_round(self):
        #every street brings a new betting round and so I think all we need to know is who goes first
        self.agents[self.button].get_action()
        #modify game state as necessary then get next player's action
        self.agents[(self.button+1)%2].get_action()

        #The assumption which I'm pretty sure is fact but I'm very tired Actions are always in pairs. The number of actions will always be in multiples of 2.

    def post_blinds(self):
        self.pot += self.agents[self.button].post_small(Game.SMALL_BLIND)
        self.pot += self.agents[(self.button+1)%2].post_big(Game.BIG_BLIND)

    def showdown(self):
        handRank0 = self.evaluator.evaluate(self.board[0], self.hands[0])
        handRank1 = self.evaluator.evaluate(self.board[0], self.hands[1])

        #Agent0 (seat1) won the pot
        if handRank0 > handRank1:
            self.agents[0].add_chips(self.pot)

        #Agent1 (seat2) won the pot
        elif handRank1 > handRank0:
            self.agents[1].add_chips(self.pot)

        #Split pot. I realize there's a rounding error here - I don't care at this time
        elif handRank0 == handRank1:
            self.agents[0].add_chips(self.pot/2)
            self.agents[1].add_chips(self.pot/2)

        else:
            print("Something went wrong at Showdown.")

        self.pot = 0

if __name__ == "__main__":
    game = Game(Agent(), Agent())
    game.start()
