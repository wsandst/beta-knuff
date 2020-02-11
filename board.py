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
starting_exit_counts = [0]*4
exit_square = [40, 10, 20, 30]

#Class for the game board data
class Board:
    """
    Class for FiaMedKnuff Board data. The pieces are represented by a tuple (x, y) where the x represents the amount of pieces, and y the player
    Members:
        board_state [List of [int]]: Represents the 40 squares of the playing board. Starting pos of a player is 10*n, exit pos is 10*n-1
        exit_states [List of [List of [int]]]: Represents the 4 exit squares for each player.
        start_counts [List of [int]]: Represents the pieces that have to yet enter the game
        exit_counts [List of [int]]: Represents the pieces that have exited the game. Not really necessary but makes for easier counting and helps with iffy start counts
        roll [Int (1:6)]: Represents the current roll for this turn
    """

    def roll_dice(self):
        self.roll = randrange(1,7)

    def __init__(self, player_count = 4, board_state = starting_board_state, exit_states = starting_exit_states, start_counts = starting_start_counts, exit_counts = starting_exit_counts):
        self.player_count = player_count
        self.board_state = copy.deepcopy(board_state)
        self.exit_states = copy.deepcopy(exit_states)
        self.start_counts = copy.deepcopy(start_counts)
        self.exit_counts = copy.deepcopy(exit_counts)
        self.roll_dice()
        self.active_player = 1
        self.ply_count = 0
        self.roll_list = [self.roll]
        #Standard rules
        self.rule_double_entry_on_six = False
        self.rule_new_roll_on_six = False

    def move(self, mv):
        #Retrieve move attributes for readability. Is a class such a bad idea? At least for readability, could do performance test

        if mv.from_state_loc < 0: #Move out piece from starting area
            self.start_counts[mv.from_player-1] -= mv.from_count
            if mv.to_player == 0: #Empty square
                self.board_state[mv.to_index] = (mv.from_count, mv.from_player)
            elif mv.to_player == mv.from_player: #Same player in both squares!
                self.board_state[mv.to_index] = (mv.to_count+mv.from_count,mv.from_player)
            else: #Took a piece
                self.start_counts[mv.to_player-1] += mv.to_count #Increment taken players start area
                self.board_state[mv.to_index] = (mv.from_count, mv.from_player)
        elif mv.from_state_loc == 0: #Moving on the standard board
            if mv.to_state_loc == 0: #Moving to a square on the standard board
                if mv.to_player == 0: #Empty square
                    self.board_state[mv.to_index] = (1, mv.from_player)
                elif mv.to_player == mv.from_player: #Same player in both squares!
                    self.board_state[mv.to_index] = (mv.to_count+1,mv.from_player)
                else: #Took a piece
                    self.start_counts[mv.to_player-1] += mv.to_count #Increment taken players start area
                    self.board_state[mv.to_index] = (1, mv.from_player)
                if mv.from_count > 1: #Remove moving piece from from pos
                    self.board_state[mv.from_index] = (mv.from_count-1, mv.from_player)
                else:
                    self.board_state[mv.from_index] = (0,0)
            elif mv.to_state_loc > 0: #Moving into the exit area
                if mv.to_index < 4: #Not an exiting piece
                    if mv.to_player == 0: #Empty square
                        self.exit_states[mv.to_state_loc-1][mv.to_index] = (1, mv.from_player)
                    else: #Another piece here, add to it
                        self.exit_states[mv.to_state_loc-1] [mv.to_index]= (mv.to_count+1,mv.from_player)
                else: #Exiting piece, increment exit counter
                    self.exit_counts[mv.from_player-1] += 1
                if mv.from_count > 1: #Remove moving piece from from pos
                    self.board_state[mv.from_index] = (mv.from_count-1, mv.from_player)
                else:
                    self.board_state[mv.from_index] = (0,0)
        elif mv.from_state_loc > 0: #Piece in exit area
            #Piece must be moving into exit area
            if mv.to_index < 4:
                self.exit_states[mv.to_state_loc-1][mv.to_index] = (mv.to_count+1,mv.from_player)
            else: #Exiting piece, increment exit counter
                self.exit_counts[mv.from_player-1] += 1
            if mv.from_count > 1: #Remove moving piece from from pos
                self.exit_states[mv.from_state_loc-1][mv.from_index] = (mv.from_count-1, mv.from_player)
            else:
                self.exit_states[mv.from_state_loc-1][mv.from_index] = (0,0)

        self.progress_turn()

    def unmove(self, mv):
        if mv.from_state_loc < 0:
            self.board_state[mv.to_index] = (mv.to_count, mv.to_player)
            self.start_counts[mv.from_player-1] += mv.from_count
            if mv.to_player != 0 and mv.to_player != mv.from_player:
                    self.start_counts[mv.to_player-1] -= mv.to_count
        
        elif mv.from_state_loc == 0:
            if mv.to_state_loc == 0:
                if mv.to_player != 0 and mv.to_player != mv.from_player:
                    self.start_counts[mv.to_player-1] -= mv.to_count
                self.board_state[mv.to_index] = (mv.to_count, mv.to_player)
                self.board_state[mv.from_index] = (mv.from_count, mv.from_player)
            else:
                if mv.to_index < 4:
                    self.exit_states[mv.from_player-1][mv.to_index] = (mv.to_count, mv.to_player)
                else: #Piece has exited
                    self.exit_counts[mv.from_player-1] -= 1
                self.board_state[mv.from_index] = (mv.from_count, mv.from_player)

        elif mv.from_state_loc > 0:
            if mv.to_index == 4: #Piece has exited
                self.exit_states[mv.from_player-1][mv.from_index] = (mv.from_count, mv.from_player)
                self.exit_counts[mv.from_player-1] -= 1
            else: #Inside the exit state
                self.exit_states[mv.from_player-1][mv.from_index] = (mv.from_count, mv.from_player)
                self.exit_states[mv.from_player-1][mv.to_index] = (mv.to_count, mv.to_player)

        self.unprogress_turn()

    def generate_moves(self, player = None, roll = None):
        #Generate valid moves for the current active player and roll, returning a List of Move

        if player is None:
            player = self.active_player
        if roll is None:
            roll = self.roll

        moves = []

        for i, piece in enumerate(self.board_state):
            if piece[1] == player:
                to_pos = i + roll
                if to_pos >= exit_square[player-1] and i < exit_square[player-1]: #Moving to exit states
                    to_index = to_pos - exit_square[player-1]
                    if to_index > 4: #Outside exit states, invalid move
                        continue
                    to_count = 0
                    to_player = 0
                    if to_index != 4:
                        to_count, to_player = self.exit_states[player-1][to_index]
                    mv = Move(piece[0], piece[1], 0, i, to_count, to_player, player, to_index)
                    moves.append(mv)
                else: #Moving to main state
                    to_pos = (i + roll) % 40
                    to_count, to_player = self.board_state[to_pos]
                    mv = Move(piece[0], piece[1], 0, i, to_count, to_player, 0, to_pos)
                    moves.append(mv)

        for i, piece in enumerate(self.exit_states[player-1]):
            if piece[1] == player:
                to_index = i + roll
                if to_index > 4: #Outside exit states, invalid move
                    continue
                to_count = 0
                to_player = 0
                if to_index != 4:
                    to_count, to_player = self.exit_states[player-1][to_index]
                mv = Move(piece[0], piece[1], player, i, to_count, to_player, player, to_index)
                moves.append(mv)

        if self.start_counts[player-1] > 0 and (roll == 1 or roll == 6):
            index = (player- 1) * 10 + self.roll - 1
            to_count, to_player = self.board_state[index]
            mv = Move(1, player, -player, 0, to_count, to_player, 0, index)
            moves.append(mv)

            if (roll == 6) and self.rule_double_entry_on_six and self.start_counts[self.active_player-1] > 1: # Double entry
                index = (player- 1) * 10
                to_count, to_player = self.board_state[index]
                mv = Move(2, player, -player, 0, to_count, to_player, 0, index)
                moves.append(mv)

        self.total_piece_count()

        return moves


    def progress_turn(self):
        if self.roll != 6 or not self.rule_new_roll_on_six:
            self.ply_count += 1
            self.active_player = self.ply_count % (self.player_count) + 1
    
        self.roll_dice()
        self.roll_list.append(self.roll)

    def unprogress_turn(self):
        self.roll_list.pop()
        self.roll = self.roll_list[-1]

        if self.roll != 6 or not self.rule_new_roll_on_six:
            self.ply_count -= 1
            self.active_player = self.ply_count % (self.player_count) + 1
                

    def print_active_pieces(self):
        print("Main board")
        for i, piece in enumerate(self.board_state):
            if piece != (0,0):
                print("{}: {}".format(i, str(piece)))

        for j, state in enumerate(self.exit_states):
            print("Exit area for player:", j)
            for i, piece in enumerate(state):
                if piece != (0,0):
                    print("{}: {}".format(i, str(piece)))

    def total_piece_count(self): #For debugging purposes
        for player in [1,2,3,4]:
            player_count = 0
            for piece in self.board_state:
                if piece[1] == player:
                    player_count += piece[0]
            for piece in self.exit_states[player-1]:
                if piece[1] == player:
                    player_count += piece[0]
            player_count += self.exit_counts[player-1]
            player_count += self.start_counts[player-1]
            if player_count != 4: #Bad bad bad
                print("Houston, we've got a problem")

    def distance_from_exit(self, player, index): #Max 40, min 0
        exit_value = exit_square[player-1]
        if index < exit_value:
	        return exit_value - index - 1
        elif index >= exit_value: 
            return 39 - index + exit_value

    def print_data(self):
        print("Board state:")
        print(self.board_state)
        print("Exit states:")
        print(self.exit_states)
        print("Pieces yet to start:")
        print(self.start_counts)
        print("Pieces exited:")

        print(self.exit_counts)
        print("Current roll:", self.roll)
        print("Current turn: {} at ply: {}".format(self.active_player, self.ply_count))
        for i, piece in enumerate(self.board_state):
            if piece[0] != 0:
                d = self.distance_from_exit(piece[1], i)
                print ("Piece from Player {} at index {} is {} squares from exit".format(piece[1], i, d))