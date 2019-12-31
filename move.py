#Helper functions for the tuple move object. Not a class due to performance reasons, Python classes are slow.
#Move object
#List: (fromindex [tuple], toindex [tuple], piecefrom [tuple], pieceto [tuple])
#Indices: tuple of (x, y) where x identifies which list (board_state, exit_states[4] or start_counts) and y is the index of the list.
#0 is board_state, 1-4 is exit_states. -1 represents the starting area
#Piece format: Tuple of format (x,y) (ex (1,4)), where the x is piececount and y is player

def get_from_player(move):
    #Gives the player of the moving piece
    return move[2][1]

def get_to_player(move):
    #Gets the player of the taken piece, 0 if no piece is taken
    return move[3][1]

def get_from_count(move):
    #Gets the piece count of moving square
    return move[2][0]

def get_to_count(move):
    #Gets the amount of pieces on the taken square, 0 if no piece taken
    return move[3][0]

def get_from_state_loc(move):
    #Returns which list the moving piece index references. -1 is start_area, 0 is board_state, 1:4 is exit_state
    return move[0][0]

def get_from_index(move):
    #Returns the index the moving piece is at.
    return move[0][1]

def get_to_state_loc(move):
    #Returns which list the moving piece index references. -1 is start_area, 0 is board_state, 1:4 is exit_state
    return move[1][0]

def get_to_index(move):
    #Returns the index the moving piece is at.
    return move[1][1]
