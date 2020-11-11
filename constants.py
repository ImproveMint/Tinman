from enum import IntEnum

class Street(IntEnum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

class Action(IntEnum):
    CHECK_FOLD = 0
    CALL = 1
    BET_RAISE = 2
