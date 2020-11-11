from spin import Spin

if __name__ == "__main__":
    blind_structure = [20, 30, 40, 60, 80, 100, 120, 150, 180, 200, 250, 300, 350, 400, 450, 500]
    hands_per_level = 6 #just a guess
    starting_stack = 300
    games = 2500

    for game in range(games):
        spin = Spin(starting_stack, blind_structure, hands_per_level)
        winner = spin.start()

        print(f"Winner Player : {winner}")
