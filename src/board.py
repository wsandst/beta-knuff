"""Board class for representing the Ludo board state"""

from random import randrange
import copy
from move import *

# Board init variables
board_size = 40
exit_size = 4
pieces_per_player = 4
starting_board_state = [(0,0)]*board_size
starting_exit_states = [[(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)], [(0,0), (0,0), (0,0), (0,0)]]
starting_start_counts = [4]*4
starting_exit_counts = [0]*4
exit_square = [40, 10, 20, 30]

# Class for the game board data
class Board:
    """
    Class for FiaMedKnuff Board data. The pieces are represented by a tuple (x, y) where the x represents the amount of pieces, and y the player
    Members:
        board_state: list of int - Represents the 40 squares of the playing board. Starting pos of a player is 10*n, exit pos is 10*n-1
        exit_states: list of (list of int) - Represents the 4 exit squares for each player.
        start_counts: list of int [0:4] - Represents the pieces that have to yet enter the game
        exit_counts: list of int [0:4] - Represents the pieces that have exited the game. Not really necessary but makes for easier counting and helps with iffy start counts
        roll : int [1:6] - Represents the current roll for this turn
        roll_list: list of int - List representing history of rolls, useful for unmove
        active_player: int - Represents which player has the current turn
        ply_count: int - Counter for the amount of turns made 
        RULES
        rule_double_entry_on_six: bool
        rule_new_roll_on_six: bool
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
        self.compact_repr = [0] * (640 + 64 + 16 + 16)

    def move(self, mv: Move):
        """ Perform move mv. Move pieces, increment counters etc"""
        
        if not mv: #Progress turn for null move and do nothing else
            self.progress_turn()
            return

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

    def unmove(self, mv : Move):
        """Unmove move mv. Does a move, but backwards"""

        if not mv: #Unprogress turn for null move and do nothing else
            self.unprogress_turn()
            return

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

    def generate_moves(self, player = None, roll = None) -> list:
        """ Generate valid moves for the current active player and roll, returning a List of Move """

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

        #self.total_piece_count()

        return moves


    def progress_turn(self):
        """ Progress turn by incrementing ply counter and switching active player """
        if self.roll != 6 or not self.rule_new_roll_on_six:
            self.ply_count += 1
            self.active_player = self.ply_count % (self.player_count) + 1
    
        self.roll_dice()
        self.roll_list.append(self.roll)

    def unprogress_turn(self):
        """ Unprogress turn by decrementing ply counter and switching active player """
        self.roll_list.pop()
        self.roll = self.roll_list[-1]

        if self.roll != 6 or not self.rule_new_roll_on_six:
            self.ply_count -= 1
            self.active_player = self.ply_count % (self.player_count) + 1
                
    def distance_from_exit(self, player : int, index : int) -> int: #Max 40, min 0
        """ Helper function. Returns distance from an index to the players own exit"""
        exit_value = exit_square[player-1]
        if index < exit_value:
	        return exit_value - index - 1
        elif index >= exit_value: 
            return 39 - index + exit_value

    # Debugging helper functions below

    def print_active_pieces(self):
        """ Debugging function. Print active pieces """
        print("Main board")
        for i, piece in enumerate(self.board_state):
            if piece != (0,0):
                print("{}: {}".format(i, str(piece)))

        for j, state in enumerate(self.exit_states):
            print("Exit area for player:", j)
            for i, piece in enumerate(state):
                if piece != (0,0):
                    print("{}: {}".format(i, str(piece)))

    def total_piece_count(self):
        """ Debugging function. Check total pieces in play per player are not more than 4"""
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
                print("Error: Current pieces in play are more than expected")

    def print_data(self):
        """ Debugging function. Print all board states """
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

    def check_win(self):
        """Returns player_id if that player has one. 0 otherwise"""
        for player, count in enumerate(self.exit_counts):
            if count == 4:
                return player + 1
        return 0

    def generate_compact_repr(self):
        """ Generates a compact floating point representation of the board 
            Used for neural networks """
        output = [0.0] * (40*2+4+4+1)
        #output[0] = self.exit_counts[0] / 4
        #output[0] = (self.active_player - 1) / 3
        output[1] = self.start_counts[0] / 4
        output[2] = self.start_counts[1] / 4
        output[3] = self.start_counts[2] / 4
        output[4] = self.start_counts[3] / 4
        output[5] = self.exit_counts[0] / 4
        output[6] = self.exit_counts[1] / 4
        output[7] = self.exit_counts[2] / 4
        output[8] = self.exit_counts[3] / 4
        for i, (count, player) in enumerate(self.board_state):
            output[i*2+9+0] = player / 4
            output[i*2+9+1] = count / 4
        return output
    
    def generate_compact_repr_hot(self):
        for index, (count, player) in enumerate(self.board_state):
            while count > 0:
                count -= 1
                self.compact_repr[index*4*4 + (player-1)*4 + count] = 1

        for player, state in enumerate(self.exit_states):
            for index, (_, count) in enumerate(state):
                while count > 0:
                    count -= 1
                    self.compact_repr[640 + player*4*4 + index*4 + count] = 1

        for index, count in enumerate(self.exit_counts):
            while count > 0:
                count -= 1
                self.compact_repr[640 + 64 + index*4 + count] = 1

        for index, count in enumerate(self.start_counts):
            while count > 0:
                count -= 1
                self.compact_repr[640 + 64 + 16 + index*4 + count] = 1

        return self.compact_repr