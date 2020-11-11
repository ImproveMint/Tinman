from random import choice
from card import Card
from deck import Deck
from evaluator import Evaluator
from time import sleep, time
from enum import IntEnum
import logging, sys
from player import Player, Action

'''
This program simulates a Pokerstars Spin and Go tournament.
A spin and go is a 3 player hyper tournament where winner takes all (typically)
A useful characteristic of spin and gos is that since winner takes all they are very similar to cash games. ChipEV is all that matters.
'''
class Street(IntEnum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

class Spin():
    #These can be constructor arguments in the future
    blind_structure = [20, 30, 40, 60, 80, 100, 120, 150, 180, 200, 250, 300, 350, 400, 450, 500]
    hands_per_level = 10
    starting_stack = 500

    def __init__(self, logging_level=logging.DEBUG):
        logging.basicConfig(stream=sys.stderr, level=logging_level)
        self.players = [Player(Spin.starting_stack, "Bob"), Player(Spin.starting_stack, "Tin"), Player(Spin.starting_stack, "Alice")]
        self.pm = PlayerManager(self.players)
        self.deck = Deck()
        #Will update to C evaluator in the future. Seems like C is 10x faster than pure python implementation.
        self.evaluator = Evaluator()
        self.board = []
        self.hands = []

        self.pot = Pot()
        self.street = Street.PREFLOP

        self.blind_level = 10
        self.BIG_BLIND = Spin.blind_structure[self.blind_level-1]
        self.SMALL_BLIND = Spin.blind_structure[self.blind_level-1]//2

        self.num_hands = 0
        self.game_state = ""

        #Experimental
        self.betting_open = True
        self.highest_bet = 0
        self.hand_over = False

    def start(self):
        while self.pm.get_remaining_players() > 1:
            #new hand
            self.__new_hand()

            print(f"Button is {self.pm.get_button().get_name()}")
            #PREFLOP
            self.__post_blinds()
            for i in range(len(self.players)):
                self.players[i].deal_hand(self.hands[i])
                self.players[i].print_player()
            #self.__betting_round()

            '''
            #FLOP
            self.__next_street()
            self.__betting_round()

            #TURN
            self.__next_street()
            self.__betting_round()

            #RIVER
            self.__next_street()
            self.__betting_round()
            '''

            print(Card.print_pretty_cards(self.board[0]))
            #SHOWDOWN
            self.__next_street()
            self.__showdown()

    def __new_hand(self):
        self.game_state = ""
        self.pot.empty() #should only be called here.
        self.street = Street.PREFLOP
        self.pm.new_hand()
        self.num_hands+=1

        self.highest_bet = 0
        self.hand_over = False

        if self.num_hands%Spin.hands_per_level == 0:
            self.__increase_blinds()

        self.deck.shuffle()
        self.board.clear()
        self.board.append(self.deck.draw(5))

        #Deals 2 cards to each remaining player
        self.hands.clear()
        for player in self.players:
            self.hands.append(self.deck.draw(2))

    def __post_blinds(self):
        self.pot.add_to_pot(self.pm.get_small_blind().post_small(self.SMALL_BLIND))
        logging.debug(f"Player {self.pm.get_small_blind().get_name()} posted small blind.")
        self.pot.add_to_pot(self.pm.get_big_blind().post_big(self.BIG_BLIND))
        logging.debug(f"Player {self.pm.get_big_blind().get_name()} posted big blind.")

    def __increase_blinds(self):
        self.blind_level+=1
        self.BIG_BLIND = Spin.blind_structure[self.blind_level-1]
        self.SMALL_BLIND = Spin.blind_structure[self.blind_level-1]//2
        logging.debug("Blinds went up")

    def __betting_round(self):
        acting_player = self.pm.first_to_act()

        while acting_player is not None:
            action = acting_player.get_action(self.game_state)
            self.__process_action(acting_player, action)
            acting_player = self.pm.next_player()

    def __next_street(self):
        if self.street == Street.PREFLOP:
            self.street = Street.SHOWDOWN
        else:
            self.street = Street.PREFLOP
        #self.street = (self.street +1)
        print(Street(self.street))
        self.pm.new_street(self.street)

    '''
    This function is modified at the moment for a simpler game where the player must fold or jam
    '''
    def __process_action(self, player, action, raise_size = 0):
        #Folded
        if action == 0:
            logging.debug(f"Player {player.get_name()} folded.")
            player.folded = True
        #Allin
        elif action == 1:
            betsize = player.bet(1500)#simplified to bet all available chips in a spin and go
            highest_bet = betsize
            self.pot.add_to_pot(betsize)
            logging.debug(f"Player {player.get_name()} is all in for {betsize}")

    def __showdown(self):
        hand_ranks = []
        #Evaluate all the hands
        for player in self.players:
            hand_ranks.append(self.evaluator.evaluate(player.get_hand(), self.board[0]))

        hand_ranks_copy = sorted(hand_ranks)

        winner_index = hand_ranks.index(hand_ranks_copy[0])
        winner = self.players[winner_index]
        if winner.folded:
            winner_index = hand_ranks.index(hand_ranks_copy[1])
            winner = self.players[winner_index]
            if winner.folded:
                winner_index = hand_ranks.index(hand_ranks_copy[2])
                winner = self.players[winner_index]
        winner.add_chips(self.pot.get_pot_size())

        print(f"{winner.get_name()} won the pot of {self.pot.get_pot_size()}")

class Pot():
    def __init__(self):
        self.main_pot = 0

    def add_to_pot(self, chips):
        self.main_pot += chips

    def empty(self):
        self.main_pot = 0

    def get_pot_size(self):
        return self.main_pot

class PlayerManager():
    def __init__(self, players):
        self.players = players
        self.__remaining_players = len(players)
        self.__button_index = choice([0,1,2])
        self.__acting_player_index = None
        self.__first_to_act = None
        self.street = None

    def move_button(self):
        self.street = Street.PREFLOP
        self.__button_index = self.players.index(self.__next_active_seat(self.__button_index))
        self.__first_to_act = self.__get_first_to_act_preflop()
        self.acting_player_index = self.players.index(self.__first_to_act)

    '''
    Returns the next active player after index
    '''
    def __next_active_seat(self, index):
        player = self.players[(index+1)%len(self.players)]
        count = 0
        while player.folded or player.allin or player.dead:
            player = self.players[(index+1)%len(self.players)]
            count+=1
            if count == 3:
                return None
        return player

    def new_hand(self):
        for player in self.players:
            if player.get_stack() == 0:
                player.dead = True
                self.players.remove(player)
                self.__remaining_players-=1
                print(f"{player.get_name()} is dead.")
        self.move_button()

    def new_street(self, street):
        self.street = street
        if street != Street.PREFLOP and street != Street.SHOWDOWN:
            self.__first_to_act = self.__get_first_to_act_postflop()
            if self.__first_to_act is None: #This is a situation where everyone is all in or folded
                return
            self.__acting_player_index = self.players.index(self.__first_to_act)
    '''
    returns the next player to act and modifies the acting player index unlike __next_active_seat
    '''
    def next_player(self):
        player = self.__next_active_seat(self.__acting_player_index)
        if player is not None:
            self.__acting_player_index = self.players.index(player)
        return player

    '''
    Returns player in the Button position
    '''
    def get_button(self):
        return self.players[self.__button_index]

    '''
    Returns player in the Small Blind position
    '''
    def get_small_blind(self):
        HU_correction = self.__HU_correction()
        index = (self.__button_index + HU_correction)%len(self.players)
        return self.__next_active_seat(index)

    '''
    Returns player in the Big Blind position
    '''
    def get_big_blind(self):
        HU_correction = self.__HU_correction()
        index = (self.__button_index + HU_correction + 1)%len(self.players)
        return self.__next_active_seat(index)

    def first_to_act(self):
        return self.__first_to_act

    def __HU_correction(self):
        HU_correction = 0
        if self.__remaining_players == 2:
            HU_correction = 1
        return HU_correction

    def __get_first_to_act_postflop(self):
        if self.get_big_blind() is None:
            return
        index = self.players.index(self.get_big_blind())
        player = self.__next_active_seat(index)
        if player is not None:
            self.__acting_player_index = self.players.index(player)
        return player

    def __get_first_to_act_preflop(self):
        HU_correction = self.__HU_correction()
        self.__acting_player_index = (self.__button_index + HU_correction + 3)%len(self.players)
        return self.players[self.__acting_player_index]

    def get_active_player(self):
        return self.players[self.__acting_player_index]

    def get_remaining_players(self):
        return self.__remaining_players

if __name__ == "__main__":
    start_time = time()
    spin = Spin()
    spin.start()
    print("--- %s seconds ---" % (time() - start_time))
