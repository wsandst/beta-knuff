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

    def __init__(self, player_count = 4, board_state = starting_board_state, exit_states = starting_exit_states, start_counts = starting_start_counts):
        self.player_count = player_count
        self.board_state = copy.deepcopy(board_state)
        self.exit_states = copy.deepcopy(exit_states)
        self.start_counts = copy.deepcopy(start_counts)
        self.roll_dice()
        self.active_player = 1
        self.ply_count = 1

    def move(self, mv):
        #Retrieve move attributes for readability. Is a class such a bad idea? At least for readability, could do performance test
        if mv.from_state_loc == -1: #Move out piece from starting area
            self.start_counts[mv.from_player-1] -= 1
            if mv.to_player == 0: #Empty square
                self.board_state[mv.to_index] = (1, mv.from_player)
            elif mv.to_player == mv.from_player: #Same player in both squares!
                self.board_state[mv.to_index] = (mv.to_count+1,mv.from_player)
            else: #Took a piece
                self.start_counts[mv.to_player-1] += 1 #Increment taken players start area
                self.board_state[mv.to_index] = (1, mv.from_player)
        elif mv.from_state_loc == 0: #Moving on the standard board
            if mv.to_state_loc == 0: #Moving to a square on the standard board
                if mv.to_player == 0: #Empty square
                    self.board_state[mv.to_index] = (1, mv.from_player)
                elif mv.to_player == mv.from_player: #Same player in both squares!
                    self.board_state[mv.to_index] = (mv.to_count+1,mv.from_player)
                else: #Took a piece
                    self.start_counts[mv.to_player-1] += 1 #Increment taken players start area
                    self.board_state[mv.to_index] = (1, mv.from_player)
                if mv.from_count > 1: #Remove moving piece from from pos
                    self.board_state[mv.from_index] = (mv.from_count-1, mv.from_player)
                else:
                    self.board_state[mv.from_index] = (0,0)

        self.progress_turn()

    def unmove(self, move):
        pass

    def generate_moves(self, player, roll):
        pass

    def progress_turn(self):
        self.active_player = self.ply_count % (self.player_count) + 1
        self.ply_count += 1
        self.roll_dice()
 
    def print_data(self):
        print("Board state:")
        print(self.board_state)
        print("Exit states:")
        print(self.exit_states)
        print("Pieces yet to start:")
        print(self.start_counts)
        print("Current roll:", self.roll)
        print("Current turn:", self.active_player, "at ply:", self.ply_count)
