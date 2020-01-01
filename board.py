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
starting_exit_counts = [4]*0

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
        self.ply_count = 1

    def move(self, mv):
        #Retrieve move attributes for readability. Is a class such a bad idea? At least for readability, could do performance test
        if mv.from_state_loc < 0: #Move out piece from starting area
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
            elif mv.to_state_loc > 0: #Moving into the exit area
                if mv.to_index < 4: #Not an exiting piece
                    if mv.to_player == 0: #Empty square
                        self.exit_states[mv.to_state_loc-1][mv.to_index] = (1, mv.from_player)
                    else: #Another piece here, add to it
                        self.exit_states[mv.to_state_loc-1] [mv.to_index]= (mv.to_count+1,mv.from_player)
                else: #Exiting piece
                    self.exit_states[mv.to_state_loc-1] += 1
                if mv.from_count > 1: #Remove moving piece from from pos
                    self.board_state[mv.from_index] = (mv.from_count-1, mv.from_player)
                else:
                    self.board_state[mv.from_index] = (0,0)
        elif mv.from_state_loc > 0: #Piece in exit area
            #Piece must be moving into exit area
            if mv.to_index < 4:
                self.exit_states[mv.to_state_loc-1][mv.to_index] = (mv.to_count+1,mv.from_player)
            else: #Exiting piece, increment exit counter
                self.exit_states[mv.to_state_loc-1] += 1
            if mv.from_count > 1: #Remove moving piece from from pos
                self.exit_states[mv.from_state_loc-1][mv.from_index] = (mv.from_count-1, mv.from_player)
            else:
                self.exit_states[mv.from_state_loc-1][mv.from_index] = (0,0)
                
            


        self.progress_turn()

    def unmove(self, move):
        pass

    def generate_moves(self, player = None, roll = None):
        #Generate valid moves for the current active player and roll, returning a List of Move
        
        if player is None:
            player = self.active_player
        if roll is None:
            roll = self.roll

        moves = []

        i = 0

        for piece in self.board_state:
            if piece[1] == player:
                to_pos = i + roll
                if i + roll < 40: #Moving to main state
                    to_count, to_player = self.board_state[to_pos]
                    mv = Move(piece[0], piece[1], 0, i, to_count, to_player, 0, to_pos)
                    moves.append(mv)
                else: #Moving to exit states
                    to_index = (to_pos - 40) % 4
                    area = (to_pos - 40) // 4
                    pass
            i += 1    


        for piece in self.exit_states:
            pass

        if self.start_counts[player-1] > 0 and (roll == 1 or roll == 6):
            index = (player- 1) * 10 + self.roll - 1
            to_count, to_player = self.board_state[index]
            mv = Move(1, player, -player, 0, to_count, to_player, 0, index)
            moves.append(mv)


        return moves


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
        print("Pieces exited:")
        print(self.exit_counts)
        print("Current roll:", self.roll)
        print("Current turn:", self.active_player, "at ply:", self.ply_count)

    def print_active_pieces(self):
        i = 0
        print("Main board")
        for piece in self.board_state:
            if piece != (0,0):
                print(i + ": " + str(piece))
            i += 1
        j = 1
        for state in self.exit_states:
            print("Exit area for player:", j)
            j += 1
            i = 0
            for piece in state:
                if piece != (0,0):
                    print(i + ": " + str(piece[0]))
                i += 1