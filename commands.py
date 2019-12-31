import board, graphics
import copy

#List of commands
command_list = """List of commands for BetaKnuff Development Build:
exit                                Exit BetaKnuff
display [-a]                        Displays the current game board and state. -e prints additional info
reset                               Resets the main board to start
roll                                Display the roll for this turn.
move <pos> [-d distance]            Move piece on pos with current roll. -d to override roll. pos is -1 starting area, 0-40 main board, 41-52 exit area
set <pos> <player> [count]          Add a piece on the board, with no regards to the game rules
"""

#This module adds commands for the command parser in main
#Flags is a dictionary containing the char flag (ex 'd') and the corresponding arg (None if none)
#The "standard" arguments, ie the ones at the start without a flag is filed under the flag "-default" 

def cmd_display(current_board, flags):
    #cmd: display
    if ('a' in flags):
        graphics.display_board(current_board)
        current_board.print_data()
    else:
        graphics.display_board(current_board)

def cmd_reset(current_board, flags):
    #cmd: reset
    current_board.board_state = copy.deepcopy(board.starting_board_state)
    current_board.exit_states = copy.deepcopy(board.starting_exit_states)
    current_board.start_counts = copy.deepcopy(board.starting_start_counts)
    current_board.roll_dice()

def cmd_roll(current_board, flags):
    #cmd: roll
    print("Roll: ", current_board.roll)

def cmd_help(flags):
    print(command_list)

def cmd_move(current_board, flags):
    pass

def cmd_set(current_board, flags):
    #cmd: set <pos> <player> [count]
    #Mandatory flag -default 2
    if "default" not in flags or len(flags["default"]) < 2:
        error_message("The required arguments are missing or are incorrectly formated")
    
    pos = int(flags["default"][0])
    player = int(flags["default"][1])
    count = 1
    if len(flags["default"]) == 3:
        count = int(flags["default"][2])

    if pos < 40 and pos >= 0:
        current_board.board_state[pos] = (count, player)
    elif pos >= 40 and pos < 56: #Exit area
        index = (pos - 40) % 4
        area = (pos - 40) // 4
        current_board.exit_states[area][index] = (count, player)
    elif pos == -1:
        current_board.start_counts[player-1] = count
    else:
        error_message("The required arguments are missing or are incorrectly formated")


def error_message(reason):
    print("Command failure: " + reason + ". Please try again.")