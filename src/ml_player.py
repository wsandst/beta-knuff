import ml_model
from player import *
import math
import numpy as np


class GenerateDataPlayer(Player):
    def __init__(self, name = "Unspecified"):
        self.name = name
        self.win_count = [0,0,0,0]
        self.has_won = False
        self.recorded_inputs = []
        self.recorded_outputs = []


    def eval_piece(self, distance: int, count = 1) -> int:
        """ Return the value of a piece at this square """
        return (39 - distance) * count
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
        return self.normalize(board, scores)

    def normalize(self, board, scores):
        winner = board.check_win()
        if winner:
            scores = [0] * 4
            scores[winner - 1] = 1
            return scores
        scores = [math.exp(score / 40) for score in scores]
        total = sum(scores)
        scores = [score / total for score in scores]
        return scores

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board)[self.player-1]
            current_board.unmove(mv)

            if score >= best_score:
                best_score = score
                best_index = i

        self.recorded_inputs.append(current_board.generate_compact_repr())
        self.recorded_outputs.append([best_score])

        return moves[best_index]

    def save_data_to_file(self, filename):
        np_inputs = np.array(self.recorded_inputs, dtype=np.float32)
        np_outputs = np.array(self.recorded_outputs, dtype=np.float32)
        np.savetxt(filename+"_inputs.txt", np_inputs)
        np.savetxt(filename+"_outputs.txt", np_outputs)

class MLPlayer(Player):
    """Player which uses a neural network evaluation function """
    def __init__(self, name = "Unspecified"):
        self.name = name
        self.win_count = [0,0,0,0]
        self.has_won = False
        self.model = ml_model.Model()

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        #self.model.generate_input(current_board)
        return moves[0]