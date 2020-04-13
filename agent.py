class Agent:
    #Should the agent have a copy of the blinds? Or just the game
    BIG_BLINDS = 100
    BIG_BLIND_IN_CENTS = 100
    players = 0

    def __init__(self):
        self.stack = self.BIG_BLINDS*self.BIG_BLIND_IN_CENTS
        self.player_name = "player" + str(self.players + 1)
        self.hand = []
        Agent.players+=1

    def add_chips(self, chips):
        #want to make sure chips is a POSITIVE and WHOLE INT. No negatives, 0s or floats.
        self.stack+=chips

    def bet(self, betsize):
        #Need to make sure that betsize is less than agent's remaning stack
        if betsize < self.stack:
            self.stack-=betsize
        elif betsize > self.stack:
            print("Player is all in")
            betsize = self.stack
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

    #This is where code needs to be inherited to allow testing of diferent AI's
    def get_action(self):
        pass

    def print_player(self):
        print(self.player_name)
        print("$" + str(self.stack/100))
