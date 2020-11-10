from enum import IntEnum
from random import choice, randint, random
from card import Card

class Action(IntEnum):
    FOLDCHECK = 1
    CALL = 2
    RAISE = 3

class Player:
    max_committed = 0
    min_raise = 0 #this is the minimum amount you can bet ABOVE the max_committed
    big_blind = 0

    def __init__(self, name, stack):
        self.stack = stack
        self.name = name
        self.hand = []
        self.allin = False
        self.dead = False
        self.committed = 0 #Integer than keeps track of how much is committed on this street.
        self.folded = False

    def add_chips(self, chips):
        #want to make sure chips is a POSITIVE and WHOLE INT. No negatives, 0s or floats.
        self.stack+=chips
        self.allin = False;

    def reset(self):
        self.folded = False
        self.allin = False

    def reset_committed(self):
        self.committed = 0
        Player.max_committed = 0
        Player.min_raise = 0

    def bet(self, betsize):
        if betsize >= self.stack:
            self.allin = True
            betsize = self.stack

        self.stack-=betsize
        self.committed+=betsize

        #this keeps track of the largest bet committed as well as min raise sizing
        if self.committed > Player.max_committed:
            difference = self.committed - Player.max_committed

            if difference > Player.big_blind:
                Player.min_raise = difference

            else:
                Player.min_raise = Player.big_blind#Little nervous about this might produce errors

            Player.max_committed = self.committed

        return betsize

    #Hate this function name it's not indicative, all it does is gives the agent their 2 hole cards
    def deal_hand(self, hand, big_blind):
        Player.big_blind = big_blind
        self.hand = hand

    #This returns the agents hand mostly for testing and visual simulations
    def get_hand(self):
        return self.hand

    def remove_from_committed(self, amount):
        if amount >= self.committed:
            removed = self.committed
            self.committed = 0
            return removed
        else:
            removed = amount
            self.committed -= amount

        return removed

    def get_stack(self):
        return self.stack

    def get_name(self):
        return self.name

    #Abstract method
    def get_action(self, gamestate):
        raise NotImplementedError("Implement this method depending on the type of intelligence of the player")

    def print_player(self):
        print(self.name, str(self.stack))
        Card.print_pretty_cards(self.hand)

    def __str__(self):
        return (self.get_name() + " $" + str(self.get_stack()))

    def __repr__(self):
        return (self.get_name() + " $" + str(self.get_stack()))

    #This is kind of suss, I'm going to make it sort by amount committed to make my payout function work well
    def __eq__(self, other):
        return self.committed == other.committed

    def __lt__(self, other):
        return self.committed < other.committed #This may be the wrong inequality
