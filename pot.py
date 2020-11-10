from evaluator import Evaluator
from card import Card

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
        players = self.__remove_folded_players(players)

        for player in players:
            sorted_ranks.append(self.eval.evaluate(player.get_hand(), board[0]))

        sorted_ranks, players = zip(*sorted(zip(sorted_ranks, players))) #Because of how I defined equivalence in player object it sorts it by committed when rank is =

        return players, sorted_ranks

    def __calculate_payouts(self, players, players_sorted_by_rank, sorted_ranks):
        player_payouts = [0,0,0,0,0,0,0,0,0,0,0,0] #Assumes at most 12 players

        for i, player in enumerate(players_sorted_by_rank):
            sidepot = 0
            committed = player.committed

            #Because the top ranking unpaid player committed x amount all other remaining players must much if they can
            for j in range(i, len(players)):
                sidepot += players[j].remove_from_committed(committed)

            #check how many players have the same ranked hand as the top ranking unpaid player
            split_count = 1
            for k in range(i, len(players_sorted_by_rank) -1):
                if sorted_ranks[k] == sorted_ranks[k+1]:
                    split_count+=1
                else:
                    break;

            #Divide the split pot amongst players with same ranked hands
            reward = sidepot/split_count
            for l in range(i, i + split_count):
                player_payouts[l] += reward

        return player_payouts

    def payout(self, players, board):
        sidepot = 0
        players_sorted_by_rank, sorted_ranks = self.__sort_players(players, board)

        player_payouts = self.__calculate_payouts(players, players_sorted_by_rank, sorted_ranks)

        for x in range(len(sorted_ranks)):
            payout = player_payouts[x]
            if payout > 0:
                players_sorted_by_rank[x].add_chips(payout)
                self.main_pot-=(payout)
            elif self.main_pot == 0:
                break

        if self.main_pot != 0:
            print(f"ERROR: Entire pot should have been paid out: ${self.main_pot} remaining")

        assert(self.main_pot == 0)

        return player_payouts, players_sorted_by_rank

    def get_pot_size(self):
        return self.main_pot

    def __str__(self):
        return str(self.main_pot)
