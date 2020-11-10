from player import Player

class mcplayer(Player):
    def get_action(self, gamestate):
        #Need some black box simulator for MC to generate search

        '''
        example - run 1000 sims of checking
        -run 1000 sims of folding
        -run 1000 sims of betting 1/2 pot
        -run 1000 sims of betting 1/3 pot
        -run 1000 sims of betting 3/4 pot
        -run 1000 sims of betting pot
        -run 1000 sims of all in
        -run 1000 sims of min raising
        -run 1000 sims of 3x raising

        something like that,

        TTC - are all actions after the action taken random? I think so
        Even though the agent should technically only receive a reward for
        winning there needs to be a way to evaluate the actions and so I
        guess it should be by EV for that hand?
        '''

        return 0, 0
