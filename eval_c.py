from ctypes import *

lib = CDLL("FastEval.dll")

lib.eval_5cards_fast.restype = c_short
lib.eval_6cards_fast.restype = c_short
lib.eval_7cards_fast.restype = c_short

lib.eval_5cards_fast.argtypes = [c_int, c_int, c_int, c_int, c_int]
lib.eval_6cards_fast.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int]
lib.eval_7cards_fast.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_int]

def evaluate5(board, hand):
    return lib.eval_5cards_fast(board[0], board[1], board[2], hand[0], hand[1])

def evaluate6(board, hand):
    return lib.eval_6cards_fast(board[0], board[1], board[2], board[3], hand[0], hand[1])

def evaluate7(board, hand):
    return lib.eval_7cards_fast(board[0], board[1], board[2], board[3], board[4], hand[0], hand[1])
