for player import *
import copy
class Node:
    """A part of a tree in MCST"""
    def __init__(self):
        self.rolls = [None]*6
        score = 0
        visits = 0


    def updateState(self, win)
        self.visits += 1
        if win:
            self.score += 1


class MontePlayer(Player):
    """An AI based on a monte carlo tree search (mcts)"""
    def __init__(self, policy):
        """Policy refers to the simulation step of the MCTS"""
        self.startNode = Node()
        self.policy = policy

    def play(self, currentBoard, moves):
        if len(moves) == 1:
            return moves[0]

    def _expand(self, board, node):

        winner = 0
        if node.rolls[board.roll] == None:
            moves = board.moves()
            node.rolls[board.roll] = {move : None for move in moves}
        

            move = self._select(node, board.roll)
            workBoard = copy.deepcopy(board)
            workBoard.move(move)
            winner = self._simulate(workBoard)
            node.rolls[board.roll][move] = Node()
            node.rolls[board.roll][move].updateState(winner == workBoard.active_player)
        else
            move = self._select(node, board.roll)
            workBoard = copy.deepcopy(board)
            workBoard.move(move)
            if node.rolls[board.roll][move] == None:
                winner = self._simulate(workBoard)
                node.rolls[board.roll][move] = Node()
                node.rolls[board.roll][move].updateState(winner == workBoard.active_player)
            else:
                winner = self._expand(workBoard, node.rolls[board.roll][move]
        node.updateState(winner == board.active_player)
        return winner

    
    def _simulate(self, board):
        pass

    def _select(self, node, roll):
        pass