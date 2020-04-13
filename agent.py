from enum import IntEnum
from random import choice
from random import randint
from card import Card

class Action(IntEnum):
    FOLDCHECK = 1
    CALLCHECK = 2
    RAISE = 3

class Agent:
    #Should the agent have a copy of the blinds? Or just the game
    BIG_BLINDS = 100
    BIG_BLIND_IN_CENTS = 100
    players = 0

    def __init__(self):
        self.stack = self.BIG_BLINDS*self.BIG_BLIND_IN_CENTS
        self.player_name = "player" + str(self.players)
        self.hand = []
        self.allin = False
        Agent.players+=1
        self.committed = 0 #Integer than keeps track of how much is commited on this street.

    def add_chips(self, chips):
        #want to make sure chips is a POSITIVE and WHOLE INT. No negatives, 0s or floats.
        self.stack+=chips

    def bet(self, betsize):
        #Need to make sure that betsize is less than agent's remaning stack
        if betsize < self.stack:
            self.stack-=betsize
        elif betsize > self.stack:
            #print("Player is all in")
            self.allin = True
            betsize = self.stack

        self.committed+=betsize
        return betsize

    #post functions return size of blind posted in the event the blind puts the user all in IE their remaining stack is less than blind amount
    def post_small(self, sb):
        return self.bet(sb)

    def post_big(self, bb):
        return self.bet(bb)

    #Hate this function name it's not indicative, all it does is gives the agent his 2 hole cards
    def dealHand(self, hand):
        self.hand = hand

    #This returns the agents hand mostly for testing and visual simulations
    def get_hand(self):
        return self.hand

    def get_stack(self):
        return self.stack

    #This is where code needs to be inherited to allow testing of different AI's
    def get_action(self, min_raise):
        random_action = choice([Action.CALLCHECK, Action.FOLDCHECK, Action.RAISE])

        #Problem is that this doesn't take into account the minraise.
        if self.stack < min_raise:
            raise_size = self.stack
            if random_action == 3:
                self.allin = True
        else:
            raise_size = randint(min_raise, self.stack)

        return random_action, raise_size

    def print_player(self):
        print(self.player_name, "$" + str(self.stack/100))
        Card.print_pretty_cards(self.hand)
