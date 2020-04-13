from random import choice
from card import Card
from deck import Deck
from evaluator import Evaluator
from agent import Agent
from agent import Action
from time import sleep
from enum import IntEnum

class Street(IntEnum):
    #At this time I'm not really using this. The next_street method just resets everything but I
    #don't think it's important the the program know which street we're on.
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

class Game:
    #In cents
    BIG_BLIND = 100
    SMALL_BLIND = 50
    min_raise = BIG_BLIND
    last_bet = 0
    player_folded = False
    player_allin = False
    street_ended = False
    street_actions = 0
    street = Street.PREFLOP

    def __init__(self, agent1, agent2):
        self.button = choice([0, 1]) #randomly chooses player that is first to act IE who is button and small blind
        self.deck = Deck()

        #Will update to C evaluator in the future. Seems like C is 10x faster than pure python implementation.
        self.evaluator = Evaluator()
        self.board = []
        self.hands = []
        self.agents = [agent1, agent2]
        self.pot = 0
        self.bet_size = 0

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
        if not Game.player_folded:
            print("-------------Flop-------------")
            Card.print_pretty_flop(self.board[0])
            self.betting_round()

        #Turn
        if not Game.player_folded:
            print("-------------Turn-------------")
            Card.print_pretty_turn(self.board[0])
            self.betting_round()

        #River
        if not Game.player_folded:
            print("-------------River-------------")
            Card.print_pretty_river(self.board[0])
            self.betting_round()

        #Showdown
        if not Game.player_folded:
            print("-------------Showdown-------------")
            self.showdown()

    def betting_round(self):
        #The program has evolved we see that both blocks of code are identical should create a loop or call same function twice
        #every street brings a new betting round and so I think all we need to know is who goes first
        while not Game.player_folded and not Game.player_allin and not Game.street_ended:
            Game.street_actions+= 1
            action, raise_size = self.agents[self.button].get_action(self.bet_size)
            self.process_action(action, raise_size)
            self.button = (self.button+1)%2

        self.next_street()
        Game.street_ended = False;

    #The assumption which I'm pretty sure is fact but I'm very tired. Actions are always in pairs. The number of actions will always be in multiples of 2.
    def process_action(self, action, raise_size):
        print("Player", self.button, ":")
        #print("Commited:", self.agents[self.button].committed)
        #print("Bet_size:", self.bet_size)
        #print(Game.street_actions)
        difference = self.bet_size - self.agents[self.button].committed

        if action == Action.CALLCHECK:
            if difference == 0:
                print("Checks")
                if Game.street_actions > 1:
                    self.next_street()
            else:
                print("Calls $" + str(difference/100))
                if Game.street_actions > 1:
                    self.pot+=difference
                    self.next_street()

        elif action == Action.FOLDCHECK:
            if difference == 0:
                print("Checks")
                if Game.street_actions > 1:
                    self.next_street()
            else:
                print("Folds")
                self.process_fold()

        elif action == Action.RAISE:
            print("Raises $", raise_size/100)
            self.pot+=raise_size
            Game.min_raise = raise_size - Game.last_bet
            Game.last_bet = raise_size
            self.bet_size = self.agents[self.button].committed + self.agents[self.button].bet(raise_size)
        else:
            print("Something is wrong at process_action")

    def process_fold(self):
        #reset all ins
        #Redeal
        self.bet_size = 0
        Game.player_folded = True
        self.agents[(self.button+1)%2].add_chips(self.pot)

        self.next_street()

    def next_street(self):
        for agent in self.agents:
            agent.committed = 0

        #reset
        Game.street_actions = 0
        self.bet_size = 0
        Game.last_bet = 0
        Game.min_raise = Game.BIG_BLIND
        Game.street_ended = True
        #Don't think we'll need this
        #Game.street = Street((int(Game.street) + 1) % 4)

    def post_blinds(self):
        self.pot += self.agents[self.button].post_small(Game.SMALL_BLIND)
        print("Player", self.button, "posted small blind.")
        self.pot += self.agents[(self.button+1)%2].post_big(Game.BIG_BLIND)
        print("Player", (self.button+1)%2, "posted big blind.")
        self.bet_size = Game.BIG_BLIND
        Game.last_bet = Game.BIG_BLIND

    def showdown(self):
        handRank0 = self.evaluator.evaluate(self.board[0], self.hands[0])
        handRank1 = self.evaluator.evaluate(self.board[0], self.hands[1])

        #Smaller handRank = better hand
        #Agent0 (seat1) won the pot
        if handRank0 < handRank1:
            print(self.agents[0].player_name, "wins a pot of $", self.pot/100)
            self.agents[0].add_chips(self.pot)

        #Agent1 (seat2) won the pot
        elif handRank1 < handRank0:
            print(self.agents[1].player_name, "wins a pot of $", self.pot/100)
            self.agents[1].add_chips(self.pot)

        #Split pot. I realize there's a rounding error here - I don't care at this time
        elif handRank0 == handRank1:
            print("Splitpot")
            self.agents[0].add_chips(self.pot/2)
            self.agents[1].add_chips(self.pot/2)

        else:
            print("Something went wrong at Showdown.")

        self.pot = 0

if __name__ == "__main__":
    game = Game(Agent(), Agent())
    game.start()
