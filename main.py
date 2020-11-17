from spin import Spin
import time

if __name__ == "__main__":
    blind_structure = [20, 30, 40, 60, 80, 100, 120, 150, 180, 200, 250, 300, 350, 400, 450, 500]
    hands_per_level = 6 #just a guess
    starting_stack = 300
    games = 1000

    start_time = time.perf_counter()

    players = {} # Number of games each player wins

    for game in range(games):
        if game%100 == 0:
            print(game)

        spin = Spin(starting_stack, blind_structure, hands_per_level)
        winner = spin.start()

        name = winner.get_name()

        if players.get(name):
            players[name] = players[name] + 1

        else:
            players[name] = 1

    end_time = time.perf_counter()
    print(f"Finished in {end_time - start_time:0.4f} seconds")
    print(players)
