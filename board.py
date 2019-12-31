from random import randrange
import copy
from move import *

#Board init variables
board_size = 40
exit_size = 4
pieces_per_player = 4
starting_board_state = [(0,0)]*board_size
starting_exit_states = [[(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)]]
starting_start_counts = [4]*4

#Class for the game board data
class Board:
    """
    Class for FiaMedKnuff Board data. The pieces are represented by a tuple (x, y) where the x represents the amount of pieces, and y the player
    Members:
        board_state [List of [int]]: Represents the 40 squares of the playing board. Starting pos of a player is 10*n, exit pos is 10*n-1
        exit_states [List of [List of [int]]]: Represents the 4 exit squares for each player.
        start_counts [List of [int]]: Represents the pieces that have to yet enter the game
        roll [Int (1:6)]: Represents the current roll for this turn
    """

    def roll_dice(self):
        self.roll = randrange(1,7)

    def __init__(self, board_state = starting_board_state, exit_states = starting_exit_states, start_counts = starting_start_counts):
        self.board_state = copy.deepcopy(board_state)
        self.exit_states = copy.deepcopy(exit_states)
        self.start_counts = copy.deepcopy(start_counts)
        self.roll_dice()

    def move(self, move):
        #Retrieve move attributes for readability. Is a class such a bad idea? At least for readability, could do performance test
        from_player = get_from_player(move)
        from_count = get_from_count(move)
        from_index = get_from_index(move)
        from_state_loc = get_from_state_loc(move)

        to_player = get_to_player(move)
        to_count = get_from_count(move)
        to_index = get_to_index(move)
        to_state_loc = get_to_state_loc(move)


        if from_state_loc == -1: #Move out piece from starting area
            self.start_counts[from_player] -= 1
            if to_player == from_player: #Same player in both squares!
                self.board_state[to_index] = (to_count+1,from_player)
            else: #Took a piece!
                self.start_counts[to_player] += 1 #Increment taken players start area
                self.board_state[move[1][1]] = (1, from_player)

        elif move[0][0] == 0:
            if move[1][0] == 0:
                pass

    def unmove(self, move):
        pass

    def generate_moves(self, player, roll):
        pass

    def print_data(self):
        print("Board state:")
        print(self.board_state)
        print("Exit states:")
        print(self.exit_states)
        print("Pieces yet to start:")
        print(self.start_counts)
        print("Current roll: ", self.roll)
