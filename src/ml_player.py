import ml_model
from player import *
import math
import numpy as np



class GenerateDataPlayer(NormRuleBasedPlayer):
    recorded_outputs = []
    recorded_inputs = []

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board)[self.player-1]

            GenerateDataPlayer.recorded_inputs.append(current_board.generate_compact_repr())
            GenerateDataPlayer.recorded_outputs.append([score])

            current_board.unmove(mv)

            if score >= best_score:
                best_score = score
                best_index = i

        # Record data
        #GenerateDataPlayer.recorded_inputs.append(current_board.generate_compact_repr())
        #score = self.eval(current_board)[self.player-1]
        #GenerateDataPlayer.recorded_outputs.append([score])

        return moves[best_index]

    def save_data_to_file(self, filename):
        testing_cutoff = int(len(GenerateDataPlayer.recorded_outputs) * 0.8)
        np_inputs = np.array(GenerateDataPlayer.recorded_inputs[:testing_cutoff], dtype=np.float32)
        np_outputs = np.array(GenerateDataPlayer.recorded_outputs[:testing_cutoff], dtype=np.float32)
        np.savetxt(filename+"_inputs.txt", np_inputs)
        np.savetxt(filename+"_outputs.txt", np_outputs)

        np_test_inputs = np.array(GenerateDataPlayer.recorded_inputs[testing_cutoff:], dtype=np.float32)
        np_test_outputs = np.array(GenerateDataPlayer.recorded_outputs[testing_cutoff:], dtype=np.float32)
        np.savetxt(filename+"_test_inputs.txt", np_test_inputs)
        np.savetxt(filename+"_test_outputs.txt", np_test_outputs)

class MLPlayer(Player):
    """Player which uses a neural network evaluation function """
    def __init__(self, name = "Unspecified", model_filename = None):
        self.name = name
        self.win_count = [0,0,0,0]
        self.has_won = False
        self.model = ml_model.Model(model_filename)

    def eval(self, board):
        np_input = np.array([board.generate_compact_repr()], dtype=np.float32)
        score = self.model.model.predict(np_input)[0][0]
        return score

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        #self.model.generate_input(current_board)
        best_index = 0
        best_score = -1000000

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board)
            current_board.unmove(mv)

            if score >= best_score:
                best_score = score
                best_index = i
            
        return moves[best_index]