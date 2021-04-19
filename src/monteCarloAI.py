from player import *
import math
class Node:
    """A part of a tree in MCTS"""
    def __init__(self):
        self.rolls = [None]*6
        self.score = 0
        self.visits = 0


    def updateState(self, win):
        self.visits += 1
        if win:
            self.score += 1


class MontePlayer(Player):
    """An AI based on a monte carlo tree search (mcts)"""
    def __init__(self, name = "unspecified", policy = RuleBasedPlayer()):
        """Policy refers to the simulation step of the MCTS"""
        self.name = name
        self.exploration_param = 2**0.5
        self.startNode = Node()
        self.policy = policy
        self.win_count = [0,0,0,0]
        self.has_won = False
        self._expand_calls = 0


    def play(self, currentBoard, moves):
        self._expand_calls = 0
        if len(moves) == 1:
            return moves[0]
        for i in range(10):
            winner = self._expand(currentBoard, self.startNode)
            self.startNode.updateState(winner == currentBoard.active_player)
        best_val = -1
        for move, node in self.startNode.rolls[currentBoard.roll - 1].items():
            if not node:
                continue
            if node.visits > best_val:
                best_val = node.visits
                winchance = node.score / node.visits
                best_move = move
        
        #print("_expand called:", self._expand_calls, "Score:", int(winchance * 100), "visits:", self.startNode.rolls[currentBoard.roll - 1][best_move].visits)
        self.startNode = Node()
        return best_move


    def _expand(self, board, node):
        self._expand_calls += 1
        winner = 0
        roll = board.roll
        active_player = board.active_player
        if node.rolls[roll - 1] == None:
            moves = board.generate_moves()
            if len(moves) == 0:
                moves = [0]
            node.rolls[roll - 1] = {move : None for move in moves}
        

            move = self._select(node, roll)
            
            board.move(move)
            winner = self._simulate(board)

            node.rolls[roll - 1][move] = Node()
            board.unmove(move)
        else:
            move = self._select(node, roll)
            if node.rolls[roll - 1][move] == None:
                node.rolls[roll - 1][move] = Node()
                board.move(move)
                winner = self._simulate(board)
                board.unmove(move)
            else:
                board.move(move)
                winner = self._expand(board, node.rolls[roll - 1][move])
                board.unmove(move)
        node.rolls[roll - 1][move].updateState(winner == active_player)
        return winner

    
    def _simulate(self, board):
        moves = []
        winner = board.check_win()
        while not winner:
            legal_moves = board.generate_moves()
            if len(legal_moves) == 0:
                board.progress_turn()
                moves.append(0)
                continue

            move = self.policy.play(board, board.generate_moves())
            board.move(move)
            moves.append(move)
            winner = board.check_win()
        for move in reversed(moves):
            if move:
                board.unmove(move)
            else:
                board.unprogress_turn()
        return winner


    def _select(self, node, roll):
        score_start = self.exploration_param * math.sqrt(math.log(max(node.visits, 1)))
        best_score = -1
        for key, nodeI in node.rolls[roll - 1].items():
            if  nodeI:
                val = nodeI.score / nodeI.visits + score_start/(math.sqrt(nodeI.visits))
            else:
                val = score_start
            if val > best_score:
                best_score = val
                best_key = key
        return best_key