from card import Card
from evaluator import Evaluator
from constants import Street

class Player:
    street_max_committed = 0
    hand_max_committed = 0
    big_blind = 0
    min_raise = 0
    evaluator = Evaluator()

    def __init__(self, name, stack):
        self.stack = stack
        self.name = name
        self.hand = []
        self.hand_ranks = [-1, -1, -1] # hand ranks for flop, river and turn
        self.allin = False
        self.dead = False
        self.hand_committed = 0 #I realize I need 2 separate commit variables. for the street to calculate min raises and another for payouts
        self.street_committed = 0 #Integer than keeps track of how much is committed on this street.
        self.folded = False

    def add_chips(self, chips):
        assert(chips > 0)
        assert(not self.folded)
        self.stack+=chips
        self.allin = False;

    '''
    Resets player parameters that must be reset every hand
    '''
    def __reset_player_state(self):
        self.folded = False
        self.allin = False
        self.hand_ranks = [-1, -1, -1]
        self.__reset_hand_committed()
        self.reset_street_committed()

    '''
    This resets the committed amounts for the hand shouldn't ever have to call
    it directly as we have a reset function that must be called between hands
    '''
    def __reset_hand_committed(self):
        self.hand_committed = 0
        Player.hand_max_committed = 0

    def reset_street_committed(self):
        self.street_committed = 0
        Player.street_max_committed = 0
        Player.min_raise = 0

    def bet(self, bet_size):
        assert(bet_size > 0)
        assert(not self.folded)

        if bet_size >= self.stack:
            self.allin = True
            bet_size = self.stack

        self.stack-=bet_size
        self.hand_committed+=bet_size
        self.street_committed+=bet_size

        self.__calculate_min_raise()

        assert(self.hand_committed > 0)
        assert(self.street_committed > 0)
        assert(Player.min_raise > 0)

        return bet_size

    def min_bet(self):
        #amount needed to match the top bet
        amount_to_match = Player.street_max_committed - self.street_committed

        #min amount needed to bet
        return amount_to_match + Player.min_raise

    def __calculate_min_raise(self):

        if self.street_committed > Player.street_max_committed:
            delta = (self.street_committed - Player.street_max_committed)

            if delta > Player.min_raise:
                Player.min_raise = delta #This is the minimum amount over the last bet you must raise

            Player.street_max_committed = self.street_committed

        if Player.min_raise < self.big_blind:
            Player.min_raise = self.big_blind

    '''
    Deal's player a new hand. At the same time it calls appropriate reset function
    to reset the necessary player parameters
    '''
    def deal_new_hand(self, hand, big_blind):
        Player.big_blind = big_blind
        self.hand = hand
        self.__reset_player_state()

    '''
    Evaluating hands is one of the most expensive functions and so we want to
    store and look up the value if we've already calculated it
    '''
    def get_hand_rank(self, board, street):

        assert(street != Street.PREFLOP)

        rank = -1;

        if street == Street.FLOP:
            if self.hand_ranks[0] != -1:
                rank = self.hand_ranks[0];
            else:
                rank = Player.evaluator.evaluate(self.hand, board[:3])
                self.hand_ranks[0] = rank

        elif street == Street.TURN:
            if self.hand_ranks[1] != -1:
                rank = self.hand_ranks[1];
            else:
                rank = Player.evaluator.evaluate(self.hand, board[:4])
                self.hand_ranks[1] = rank

        else:
            if self.hand_ranks[2] != -1:
                rank = self.hand_ranks[2];
            else:
                rank = Player.evaluator.evaluate(self.hand, board)
                self.hand_ranks[2] = rank

        return rank

    def remove_from_committed(self, amount):

        remove = 0

        if amount >= self.hand_committed:
            removed = self.hand_committed
            self.hand_committed = 0

        else:
            removed = amount
            self.hand_committed -= amount

        assert(removed >= 0)

        return removed

    '''
    Checks if this player has the option to check IE, they've matched the highest
    bet. If not then player folds
    '''
    def can_check(self):
        return self.street_committed == Player.street_max_committed

    #This returns the agents starting hand
    def get_hand(self):
        return self.hand

    def get_name(self):
        return self.name

    def get_stack(self):
        return self.stack

    #Abstract method
    def get_action(self, gamestate):
        raise NotImplementedError("Implement this method depending on the type of intelligence of the player")

    def print_player(self):
        print(self.name, str(self.stack))
        Card.print_pretty_cards(self.hand)

    def __str__(self):
        return (self.get_name() + " chips (" + str(self.get_stack()) + ")")

    def __repr__(self):
        return (self.get_name() + " chips (" + str(self.get_stack()) + ")")

    #This is kind of suss, I'm going to make it sort by amount committed to make my payout function work well
    def __eq__(self, other):
        return self.hand_committed == other.hand_committed

    def __lt__(self, other):
        return self.hand_committed < other.hand_committed #This may be the wrong inequality
