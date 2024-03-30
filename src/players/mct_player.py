from player import *
import math

class Node:
    """A part of a tree in MCTS"""
    def __init__(self):
        self.rolls = [None]*6
        self.scores = [0] * 4
        self.visits = 0


    def updateState(self, results):
        self.visits += sum(results)
        self.scores = [
            score + result for score, result in zip(self.scores, results)
        ]


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
        self.exit_squares = [40, 10, 20, 30]


    def eval_piece(self, distance: int, count = 1) -> int:
        """ Return the value of a piece at this square """
        return (40 - distance) * count
        #return (10 + distance) * count



    def eval_threats(self, current_board: board.Board, index: int, player: int) -> int:
        """Measures how many pieces are within taking range of this piece, 
        and gives 1/6 of their piece values"""
        score = 0
        exit_square = self.exit_squares[player-1]
        distance = current_board.distance_from_exit(player, index)
        count, _dummy = current_board.board_state[index]
        this_piece_value = self.eval_piece(distance, count)
        for i in range(1, 7):
            index2 = (index + i) % 40
            if index2 == exit_square:
                break
            count2, player2 = current_board.board_state[index2] #in front
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score += self.eval_piece(distance, count2)
            index2 = (index - i) % 40
            count2, player2 = current_board.board_state[index2] #behind
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score -= this_piece_value * 2
        return score // 12


    def eval(self, board):
        """Evaluate the current position by analyzing the board state with rule-based logic"""
        scores = [0] * 4
        #Go through the main state and give points based on distance from the exit area
        for index, piece in enumerate(board.board_state):
            player = piece[1]
            if player != 0:
                distance_from_exit = board.distance_from_exit(player, index)
                count = piece[0]
                player -= 1
                scores[player] += self.eval_piece(distance_from_exit, count)
                scores[player] += self.eval_threats(board, index, player + 1)
        
        #Give 60 points for every piece in the exit state
        for player, state in enumerate(board.exit_states, 1):
            for piece in state:
                if piece[1] != 0:
                    count = piece[0]
                    scores[player - 1] += 60 * count

        # Give 70 points for every piece that has exited
        for player, count in enumerate(board.exit_counts, 1):
            scores[player - 1] += 80 * count
        return scores
        results = [
            scores[i] - max(
            [score for j, score in enumerate(scores) if j != i]
            ) for i in range(4)
        ]
        return results


    def play(self, board, moves):
        #print(f"score: {self.eval(board)} for player {self._current_player}")
        self._expand_calls = 0
        if len(moves) == 1:
            return moves[0]
        for _i in range(500):
            scores = self._expand(board, self.startNode)
            self.startNode.updateState(scores)
        best_val = -1
        for move, node in self.startNode.rolls[board.roll - 1].items():
            if not node:
                continue
            if node.visits > best_val:
                best_val = node.visits
                best_move = move
        
        #print("_expand called:", self._expand_calls, "Score:", int(winchance * 100), "visits:", self.startNode.rolls[currentBoard.roll - 1][best_move].visits)
        self.startNode = Node()
        return best_move


    def _expand(self, board, node):
        winner = board.check_win()
        if winner != 0:
            scores = [0] * 4
            scores[winner - 1] = 1
            return scores
        roll = board.roll
        if node.rolls[roll - 1] == None:
            moves = board.generate_moves()
            if len(moves) == 0:
                moves = [0]
            node.rolls[roll - 1] = {move : None for move in moves}
            player = board.active_player
            best_scores = [-100000] * 4
            #scores_sum = [0] * 4
            for move in moves:
                board.move(move)
                scores = self._simulate(board)
                new_node = Node()
                new_node.updateState(scores)
                #scores_sum = [s1 + s2 for s1, s2 in zip(scores_sum, scores)]
                node.rolls[roll - 1][move] = new_node
                if scores[player - 1] > best_scores[player - 1]:
                    best_scores = scores
                board.unmove(move)
            return best_scores
        else:
            move = self._select(node, roll, board.active_player)
            board.move(move)
            scores = self._expand(board, node.rolls[roll - 1][move])
            board.unmove(move)
        node.rolls[roll - 1][move].updateState(scores)
        return scores

    
    def _simulate(self, board):
        winner = board.check_win()
        if winner:
            scores = [0] * 4
            scores[winner - 1] = 1
            return scores
        scores = self.eval(board)
        scores = [math.exp(score / 40) for score in scores]
        total = sum(scores)
        scores = [score / total for score in scores]
        return scores
        """
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
        return winner"""


    def _select(self, node, roll, player):
        score_start = self.exploration_param * math.sqrt(math.log(max(node.visits, 1)))
        best_score = -1
        for key, nodeI in node.rolls[roll - 1].items():
            if  nodeI:
                val = nodeI.scores[player - 1] / nodeI.visits + score_start/(math.sqrt(nodeI.visits))
            else:
                val = score_start
            if val > best_score:
                best_score = val
                best_key = key
        return best_key