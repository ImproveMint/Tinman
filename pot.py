from evaluator import Evaluator
from card import Card
import copy

class Pot():
    def __init__(self):
        self.main_pot = 0
        self.eval = Evaluator()

    def add_to_pot(self, player, chips):
        betsize = player.bet(chips)
        self.main_pot += betsize
        return betsize

    def __remove_folded_players(self, players):
        for player in players:
            if player.folded:
                players.remove(player)

        return players

    #Sort players by hand rank and then by amount committed to pot
    def __sort_players(self, players, board):
        sorted_ranks = []
        sorted_players = self.__remove_folded_players(players)

        for player in sorted_players:
            sorted_ranks.append(self.eval.evaluate(player.get_hand(), board[0]))

        sorted_ranks, sorted_players = zip(*sorted(zip(sorted_ranks, players))) #Because of how I defined equivalence in player object it sorts it by committed when rank is =

        return sorted_players, sorted_ranks

    def __calculate_payouts(self, players, players_sorted_by_rank, sorted_ranks):
        player_payouts = [0,0,0,0,0,0,0,0,0,0,0,0] #Assumes at most 12 players

        for i, player in enumerate(players_sorted_by_rank):
            sidepot = 0
            committed = player.hand_committed

            #Because the top ranking unpaid player committed x amount all other remaining players must match if they can
            for j in range(0, len(players)):
                remove = players[j].remove_from_committed(committed)
                sidepot += remove

            #check how many players have the same ranked hand as the top ranking unpaid player
            split_count = 1
            for k in range(i, len(players_sorted_by_rank) -1):
                if sorted_ranks[k] == sorted_ranks[k+1]:
                    split_count+=1
                else:
                    break;

            #Divide the split pot amongst players with same ranked hands
            reward = sidepot//split_count
            sum = 0
            for l in range(i, i + split_count):
                player_payouts[l] += reward

        return player_payouts

    def payout(self, players, board):
        #We do this so we can keep all the player list in it's orginal state
        players_copy = []
        for player in players:
            players_copy.append(player)

        players_sorted_by_rank, sorted_ranks = self.__sort_players(players_copy, board)
        player_payouts = self.__calculate_payouts(players, players_sorted_by_rank, sorted_ranks)

        #There's a 'bug' where when it does split pots we get fractional numbers
        #Which the program doesn't allow for so we simple check was the roundoff error
        #is and then add the difference from the pot to the winning player.
        sum = 0
        for p in player_payouts:
            sum+=p

        if sum != self.main_pot:
            #print(f"Pot differs in size {self.main_pot - sum}")
            player_payouts[0]+=(self.main_pot - sum)

        for x in range(len(sorted_ranks)):
            payout = player_payouts[x]
            if payout > 0:
                players_sorted_by_rank[x].add_chips(payout)
                self.main_pot-=(payout)

            elif self.main_pot == 0:
                break

        assert(self.main_pot == 0)

        return player_payouts, players_sorted_by_rank

    def get_pot_size(self):
        return self.main_pot

    def __str__(self):
        return str(self.main_pot)
