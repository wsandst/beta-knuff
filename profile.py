from board import Board
import time
import copy

def testPerf(board, depth):
    if depth <= 0:
        return 1
    numMoves = 0
    moves = board.generate_moves()
    for move in moves:
        oldBoard = copy.deepcopy(board)
        board.move(move)
        numMoves += testPerf(board, depth - 1)
        board = oldBoard
    if len(moves) == 0:
        board.progress_turn()
        numMoves += testPerf(board, depth - 1)
    return numMoves


start = time.perf_counter()
board = Board()

nodes = testPerf(board, 35)
end = time.perf_counter()
print("Performed ", nodes/(end - start), " leaf nodes per second")