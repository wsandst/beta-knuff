class Move:
    """
    Class for move data. There are 8 int attributes
    Members:
        from_count [int]: Represents the amount of pieces in the moving square.
        from_player [int]: Represents the moving piece player. 1-4.
        from_state_loc [int]: Represents the board "state" the moving piece is moving from. 0 is board_state, 1-4 is exit_states. -1 represents the starting area
        from_index [int]: Represents the index of the state location of the form player
        to_count [int]: Represents the amount of pieces in the moving square.
        to_player [int]: Represents the taken piece player. 0 if no piece
        to_state_loc [int]: Represents the board "state" the moving piece is moving to. 0 is board_state, 1-4 is exit_states. -1 represents the starting area
        to_index [int]: Represents the index of the state location of the to square
    """
    def __init__(self, from_count = 0, from_player = 0, from_state_loc = 0, from_index = 0, to_count = 0, to_player = 0, to_state_loc = 0, to_index = 0):
        self.from_count = from_count
        self.from_player = from_player
        self.from_state_loc = from_state_loc
        self.from_index = from_index
        self.to_count = to_count
        self.to_player = to_player
        self.to_state_loc = to_state_loc
        self.to_index = to_index


    def __hash__(self):
        return self.from_count ^ self.from_player ^ self.from_state_loc ^ self.from_index ^ self.to_count ^ self.to_player ^ self.to_state_loc ^ self.to_index