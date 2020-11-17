from evaluator import Evaluator
from card import Card

class Pot():
    def __init__(self):
        self.main_pot = 0
        self.eval = Evaluator()

    def add_to_pot(self, player, chips):
        assert(not player.folded)
        assert(chips > 0)

        betsize = player.bet(chips)
        self.main_pot += betsize

        return betsize

    def get_pot_size(self):
        return self.main_pot

    def payout(self, all_players, board):

        #Create a list of players that are eligible to win the pot
        eligible_players = []
        for player in all_players:
            eligible_players.append(player)

        eligible_players = self.__remove_folded_players(eligible_players) #removes all the folded players IE keeps players eligible to win the pot
        eligible_players, sorted_ranks = self.__sort_players(eligible_players, board) #Sorts the eligible players by hand rank and then by amount committed
        player_payouts = self.__calculate_payouts(all_players, eligible_players, sorted_ranks)

        for x in range(len(sorted_ranks)):
            payout = player_payouts[x]
            if payout > 0:
                self.__payout_player(eligible_players[x], payout)
                self.main_pot-=(payout)

            elif self.main_pot == 0:
                break

        assert(self.main_pot <= 2)

        return player_payouts, eligible_players

    #Because folded players are not eligible to win the pot they are removed
    def __remove_folded_players(self, players):

        active_players = []

        for player in players:
            if not player.folded:
                active_players.append(player)

        return active_players

    #Sort players by handrank and then by amount committed to pot
    def __sort_players(self, players, board):
        sorted_ranks = []
        sorted_players = []

        for player in players:
            sorted_ranks.append(self.eval.evaluate(player.get_hand(), board[0]))

        sorted_ranks, sorted_players = zip(*sorted(zip(sorted_ranks, players))) #Because of how I defined equivalence in player object it sorts it by committed when rank is =

        return sorted_players, sorted_ranks

    def __calculate_payouts(self, players, players_sorted_by_rank, sorted_ranks):

        assert(len(players) > 1) #Should always have 2 or more players
        assert(len(players_sorted_by_rank) >= 1)

        player_payouts = [0] * len(players_sorted_by_rank)

        for i, player in enumerate(players_sorted_by_rank):
            sidepot = 0
            committed = player.hand_committed

            #Because the top ranking unpaid player committed x amount all other remaining players must match if they can
            for j in range(0, len(players)):
                removed = players[j].remove_from_committed(committed)
                sidepot += removed

            #check how many players have the same ranked hand as the top ranking unpaid player
            split_count = 1
            for k in range(i, len(players_sorted_by_rank) -1):
                if sorted_ranks[k] == sorted_ranks[k+1]:
                    split_count+=1
                else:
                    break

            #Divide the split pot amongst players with same ranked hands
            #A minor bug occurs due to roundoff error. This is ignored as it's
            #an insignificant amount relative to the blinds
            payout = sidepot//split_count

            for l in range(i, i + split_count):
                player_payouts[l] += payout

        return player_payouts

    def __payout_player(self, player, amount):
        #print(f"{player.get_name()} was paid out {amount} chips")
        player.add_chips(amount)

    def __str__(self):
        return str(self.main_pot)
