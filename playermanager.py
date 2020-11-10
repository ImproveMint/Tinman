'''
The PlayerManager class keeps track of who's turn it is to act aswell
as positioning and moving of blinds

PlayerManager might be a misnomer? Can't think of a better name but I'm
just thinking that playermanager doesn't like manager players money or actions
just who goes when and who's in which position
'''
from random import randrange
from street import Street

class PlayerManager():
    def __init__(self, players):
        self.players = players
        self.__remaining_players = len(players)
        self.__button_index = randrange(len(players))#randomly picks a player to be the button
        self.__acting_player_index = None
        self.street = None

    def move_button(self):
        self.__button_index = (self.__button_index + 1)%len(self.players)

    '''
    This returns the player who is first to act on a given street
    '''
    def first_to_act(self, street):
        self.street = street

        if street is Street.PREFLOP:
            return self.__first_to_act_preflop()
        else:
            return self.__first_to_act_postflop()

    def __first_to_act_preflop(self):
        HU_correction = self.__HU_correction()
        index = (self.__button_index + HU_correction + 3)%len(self.players)
        self.__acting_player_index = index
        return self.players[index]

    def __first_to_act_postflop(self):
        index = (self.__button_index + 1)%len(self.players)
        self.__acting_player_index = index
        return self.players[index]

    '''
    This method is a little tricky because it depends on whether it is
    pre or post flop. By calling first_to_act methods the __acting_player_index
    is changed which affects this method. That may work but seems prone to errors
    '''
    def next_player(self):
        self.__acting_player_index = (self.__acting_player_index + 1)%len(self.players)
        return self.players[self.__acting_player_index]

    '''
    Returns player in the Button position
    '''
    def get_button(self):
        return self.players[self.__button_index]

    '''
    Returns player in the Small Blind position
    This should only get called preflop so checking for allin/folded/dead players not an issue
    '''
    def get_small_blind(self):
        HU_correction = self.__HU_correction()
        return self.players[(self.__button_index + HU_correction + 1)%len(self.players)]

    '''
    Returns player in the Big Blind position
    This should only get called preflop so checking for allin/folded/dead players not an issue
    '''
    def get_big_blind(self):
        HU_correction = self.__HU_correction()
        return self.players[(self.__button_index + HU_correction + 2)%len(self.players)]

    '''
    Poker positioning changes slightly when there are 2 players (Heads up) remaining This
    calculates the necessary correction
    '''
    def __HU_correction(self):
        HU_correction = 0
        if self.__remaining_players == 2:
            HU_correction = 1
        return HU_correction
