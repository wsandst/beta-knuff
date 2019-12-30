from random import randrange

#Board init variables
board_size = 40
exit_size = 4
pieces_per_player = 4
starting_board_state = [0]*board_size
starting_exit_states = [[0]*exit_size]*4
starting_start_counts = [4]*4

#Class for the game board data
class Board:
    """
    Class for FiaMedKnuff Board data. The pieces are represented by an integer (ex 14) where the first number denotes the amount of pieces,
    and the second denotes which player the piece belongs to (1, 2, 3, 4).  
    Members:
        board_state [List of [int]]: Represents the 40 squares of the playing board. Starting pos of a player is 10*n, exit pos is 10*n-1
        exit_states [List of [List of [int]]]: Represents the 4 exit squares for each player.
        start_counts [List of [int]]: Represents the pieces that have to yet enter the game
        roll [Int (1:6)]: Represents the current roll for this turn
    """

    def roll(self):
        return randrange(1,7)

    def __init__(self, board_state = starting_board_state, exit_states = starting_exit_states, start_counts = starting_start_counts):
        self.board_state = board_state
        self.exit_states = exit_states
        self.start_counts = start_counts
        self.roll = self.roll()

    def move(self, move):
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
