from random import choice
from card import Card
from deck import Deck
from evaluator import Evaluator
from time import sleep, time
from enum import IntEnum
from pot import Pot
import logging, sys
from player import Player
from mcplayer import mcplayer
from randomplayer import randomplayer
from playermanager import PlayerManager
from constants import Street, Action

'''
This program simulates a Pokerstars Spin and Go tournament.
A spin and go is a 3 player hyper tournament where winner takes all (typically)
A useful characteristic of spin and gos is that since winner takes all they are very similar to cash games. ChipEV is all that matters.
'''

class Spin():
    def __init__(self, starting_stack, blind_structure, hands_per_level, logging_level=logging.INFO):
        logging.basicConfig(stream=sys.stderr, level=logging_level)
        self.starting_stack = starting_stack
        self.blind_structure = blind_structure
        self.hands_per_level = hands_per_level

        self.players = [randomplayer("A", self.starting_stack),
                        randomplayer("B", self.starting_stack),
                        randomplayer("C", self.starting_stack)]

        self.pm = PlayerManager(self.players)

        self.pot = Pot()
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.board = []
        self.hands = []

        self.street = Street.PREFLOP

        self.blind_level = 1 #Uses 1 indexing not 0 indexing
        self.BIG_BLIND = self.blind_structure[self.blind_level-1]
        self.SMALL_BLIND = self.blind_structure[self.blind_level-1]//2

        self.num_hands = 0
        self.game_state = ""

        self.players_in_hand = 0

    def start(self):
        #Play until there is only one player remaining IE 1 player has all the chips
        while len(self.players) > 1:
            #new hand
            self.__prepare_new_hand()

            #PREFLOP
            self.__deal_new_hand()
            self.__post_blinds()#in a real game players post blinds first, it's a small formality that doesn't matter here
            self.__betting_round()

            #FLOP
            self.__betting_round()

            #TURN
            self.__betting_round()

            #RIVER
            self.__betting_round()

            #SHOWDOWN
            self.pot.payout(self.players, self.board)
            self.remove_eliminated_players()

        return self.players[0]

    def remove_eliminated_players(self):
        before = len(self.players)
        self.players[:] = [x for x in self.players if x.get_stack() > 0]
        after = len(self.players)
        logging.debug(f"{before-after} players removed from game.")

    '''
    This method resets all variables to be able to start a new hand and does
    housekeeping of the button and blinds
    '''
    def __prepare_new_hand(self):
        self.game_state = ""
        self.street = Street.PREFLOP
        self.num_hands+=1
        self.players_in_hand = len(self.players)

        self.pm.move_button()

        logging.debug(f"----------Hand #{self.num_hands}-------------")

        if self.num_hands%self.hands_per_level == 0:
            self.__increase_blinds()

    '''
    shuffles the deck and deals a starting hand to each remaining player
    as well as the board even though it's not technically visible to the players yet

    This method also resets the player variables while we deal them a new hand
    seems like a weird place to have that but it's kind of like in order for a
    player to get a new hand they need to reset their hand status (variables)
    '''
    def __deal_new_hand(self):
        self.deck.shuffle()
        self.board.clear()
        self.board.append(self.deck.draw(5))

        #Deals 2 cards to each remaining player
        self.hands.clear()

        for i, player in enumerate(self.players):
            self.hands.append(self.deck.draw(2))
            self.players[i].deal_new_hand(self.hands[i], self.BIG_BLIND)

    def __post_blinds(self):
        self.pot.add_to_pot(self.pm.get_small_blind(), self.SMALL_BLIND)
        logging.debug(f"Player {self.pm.get_small_blind().get_name()} posted ${self.SMALL_BLIND} small blind.")
        self.pot.add_to_pot(self.pm.get_big_blind(), self.BIG_BLIND)
        logging.debug(f"Player {self.pm.get_big_blind().get_name()} posted ${self.BIG_BLIND} as big blind.")

    def __increase_blinds(self):
        logging.debug(f"Blind level: {self.blind_level}")
        self.blind_level+=1
        self.BIG_BLIND = self.blind_structure[self.blind_level-1]
        self.SMALL_BLIND = self.blind_structure[self.blind_level-1]//2
        logging.debug("Blinds went up")

    def __betting_round(self):
        #keeps track of how many player actions were taken, it's used to ensure
        #that everyone gets at least 1 chance to act. Otherwise preflop when
        #everyone just calls the big blind doesn't get option to bet

        #There has to be more than 1 player that can act to continue
        if self.__can_players_act() > 1:
            actions = 0
            acting_player = self.pm.first_to_act(self.street)

            while ((not self.__is_betting_completed()) or (actions < len(self.players))) and (self.players_in_hand > 1):
                action, betsize = acting_player.get_action(self.game_state)
                self.__process_action(acting_player, action, betsize)
                acting_player = self.pm.next_player()
                actions+=1

            #After the betting round we reset the amount committed by players
            for player in self.players:
                player.reset_street_committed()

        #Once the betting round is over we can increment street
        self.__next_street()

    '''
    This method checks that all the players for the current betting round are
    either folded, all in or have matched the required bet
    '''
    def __is_betting_completed(self):
        complete = True

        for player in self.players:
            if not(player.folded or player.allin or (player.street_committed >= Player.street_max_committed)):
                complete = False

        return complete

    '''
    This method checks how many of the remaining players can take an action
    We have to check this because otherwise we enter into betting rounds when
    we shouldn't
    '''
    def __can_players_act(self):
        act_count = 0 #Number of players who can still take legal actions in given hand

        for player in self.players:
            if (not player.folded) and (not player.allin):
                act_count+=1

        return act_count

    def __next_street(self):
        self.street = (self.street +1)
        logging.debug(Street(self.street))

    def __process_action(self, player, action, bet_size = 0):
        #Folded or checked
        if action == Action.CHECK_FOLD:

            if player.can_check():
                logging.debug(f"Player {player.get_name()} checked.")

            else:
                logging.debug(f"Player {player.get_name()} folded.")
                player.folded = True
                self.players_in_hand -= 1

        elif action == Action.CALL:
            logging.debug(f"Player {player.get_name()} called ${bet_size}")
            self.pot.add_to_pot(player, bet_size)

        elif action == Action.BET_RAISE:
            logging.debug(f"Player {player.get_name()} bet/raised ${bet_size}")
            self.pot.add_to_pot(player, bet_size)
