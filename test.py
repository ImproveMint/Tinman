from playermanager import PlayerManager
from constants import Street
from player import Player
from spin import Spin
from pot import Pot
from deck import Deck

def test_player_manager():
    print("TESTING PLAYER MANAGER CLASS")
    #Players must be named like this to do the testing
    p1 = Player("0", 100)
    p2 = Player("1", 100)
    p3 = Player("2", 100)

    players_2 = [p1, p2]
    players_3 = [p1, p2, p3]

    pm2 = PlayerManager(players_2)
    pm3 = PlayerManager(players_3)

    print("2 player game")
    print("-------------------------------")
    for x in players_2:
        button = pm2.get_button()
        sb = pm2.get_small_blind()
        bb = pm2.get_big_blind()
        first_to_act_preflop = pm2.first_to_act(Street.PREFLOP)
        first_to_act_postflop = pm2.first_to_act(Street.FLOP)

        assert(sb is button)
        #print("Small blind position: passed")

        assert(int(bb.get_name()) == (int(button.get_name())+1)%len(players_2))
        #print("Big blind position: passed")

        assert(first_to_act_preflop is button)
        #print("First to act preflop: passed")

        assert(first_to_act_postflop is bb)
        #print("First to act postflop: passed")

        pm2.move_button()
        button = pm2.get_button()

        #after we move the button the new button should be the old sb
        assert(button is bb)
        #print("Move button: passed")
    print("Player positions for 2 player game: 5/5 Tests Passed!")
    print()

    print("3 player game")
    print("-------------------------------")
    for x in players_3:
        button = pm3.get_button()
        sb = pm3.get_small_blind()
        bb = pm3.get_big_blind()
        first_to_act_preflop = pm3.first_to_act(Street.PREFLOP)
        first_to_act_postflop = pm3.first_to_act(Street.FLOP)

        assert(int(sb.get_name()) == (int(button.get_name())+1)%len(players_3))
        #print("Small blind position: passed")

        assert(int(bb.get_name()) == (int(button.get_name())+2)%len(players_3))
        #print("Big blind position: passed")

        assert(first_to_act_preflop is button)
        #print("First to act preflop: passed")

        assert(first_to_act_postflop is sb)
        #print("First to act postflop: passed")

        pm3.move_button()
        button = pm3.get_button()

        #after we move the button the new button should be the old sb
        assert(button is sb)
        #print("Move button: passed")

    print("Player positions for 3 player game: 5/5 Tests Passed!")

    for x in players_3:
        button = pm3.get_button()

def test_pot():
    #This class is hard it should test sooo many situations I'll list some
    #write tests for them as I go

    #1 player wins
    #1 player wins but one player that contributing to pot Folded
    #2 way split with 3 players
    #2 way split with 2 players
    #player is all in from posting small blind -wins/loses
    #player is all in from posting big blind -wins/loses
    #everyone folds PREFLOP
    #the winning player doesn't cover everyone
    #situation with 3 side pots. IE the player with the most chips has the worst hand, player with least chips has best hand. and etc for middle hand

    print("TESTING POT CLASS")
    stack = 100
    bet = 10
    p1 = Player("0", stack)
    p2 = Player("1", stack)
    p3 = Player("2", stack)

    players = [p1, p2, p3]

    print("testing 3 way split")
    pot = Pot()

    deck = Deck()
    deck.shuffle()

    board = []
    hand = deck.draw(2)
    board.append(deck.draw(5))

    #Note all 3 players are given the same hand which is not realistic but shouldn't matter
    p1.deal_new_hand(hand, 1)
    p2.deal_new_hand(hand, 1)
    p3.deal_new_hand(hand, 1)

    pot.add_to_pot(p1, bet)
    pot.add_to_pot(p2, bet)
    pot.add_to_pot(p3, bet)

    assert(p1.get_stack() == stack - bet)
    assert(p2.get_stack() == stack - bet)
    assert(p3.get_stack() == stack - bet)

    assert(pot.get_pot_size() == 3*bet)

    pot.payout(players, board)

    print(f"p1 stack: {p1.get_stack()}")

    assert(p1.get_stack() == stack)
    assert(p2.get_stack() == stack)
    assert(p3.get_stack() == stack)

    assert(pot.get_pot_size() == 0)

    print("Pot class: 8/8 tests passed")

if __name__ == "__main__":
    test_player_manager()
    test_pot()
