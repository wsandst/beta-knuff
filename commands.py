import board, graphics, move
import copy

#List of commands
command_list = """List of commands for BetaKnuff Development Build:
exit                                Exit BetaKnuff
help                                Lists commands for BetaKnuff
display [-a]                        Displays the current game board and state. -e prints additional info
reset                               Resets the main board to start
roll [-f num]                       Display the roll for this turn. -f forces a reroll to specified number
move <pos> [-d distance] [-f]       Move piece on pos with current roll. -d to override roll. -f to ignore restrictions. pos: -1 starting area, 0-40 main board, 41-52 exit area
moves                               Lists valid moves this turn
pass                                Skips this players turn. Used when no moves are available
set <pos> <player> [count]          Add a piece on the board, with no regards to the game rules
"""

#This module adds commands for the command parser in main
#Flags is a dictionary containing the char flag (ex 'd') and the corresponding arg (None if none)
#The "standard" arguments, ie the ones at the start without a flag is filed under the flag "-default" 

def cmd_display(current_board, flags):
    #cmd: display [-a]
    graphics.display_board(current_board)
    if 'a' in flags:
        current_board.print_data()
    if 'p' in flags:
        current_board.print_active_pieces()

def cmd_reset(current_board, flags):
    #cmd: reset
    current_board.board_state = copy.deepcopy(board.starting_board_state)
    current_board.exit_states = copy.deepcopy(board.starting_exit_states)
    current_board.start_counts = copy.deepcopy(board.starting_start_counts)
    current_board.roll_dice()

def cmd_roll(current_board, flags):
    #cmd: roll [-f roll]
    if "f" in flags:
        current_board.roll = int(flags["f"])
    print("Roll: ", current_board.roll)

def cmd_turn(current_board, flags):
    #cmd: turn [-f turn]
    if "f" in flags:
        current_board.active_player = int(flags["f"])
    print("Turn: ", current_board.active_player)

def cmd_help(flags):
    #cmd: help
    print(command_list)

def cmd_exit(flags):
    #cmd: exit
    print("Exiting BetaKnuff...")
    exit()

def cmd_move(current_board, flags):
    #cmd: move <pos> [-d distance]
    if "default" not in flags or len(flags["default"]) < 1:
        error_message("The required arguments are missing or are incorrectly formated")
        return
    if flags["default"] == "start":
        pos = -1
    elif flags["default"] == "pass":
        cmd_pass(current_board, flags)
        return
    else:
        pos = int(flags["default"])

    mv = move.Move()

    roll = current_board.roll
    if "d" in flags:
        roll = int(flags["d"])

    if pos < 40 and pos >= 0:
        mv.from_state_loc = 0
        mv.from_index = pos
        mv.from_count, mv.from_player = current_board.board_state[pos]
        new_index = mv.from_index + roll
        if new_index < 40 and new_index >= 0:
            mv.to_index = new_index
            mv.to_state_loc = 0
            mv.to_count, mv.to_player = current_board.board_state[mv.to_index]
        elif new_index >= 40 and new_index < 56:
            index = (new_index - 40) % 4
            area = (new_index - 40) // 4
            mv.to_state_loc = area+1
            mv.to_index = index
            mv.to_count, mv.to_player = current_board.exit_states[area][index]
        if "f" not in flags and current_board.board_state[mv.from_index][1] == 0:
            error_message("Invalid move - no piece in selected square")
            return
        if "f" not in flags and mv.from_player != current_board.active_player:
            error_message("Invalid move - piece does not belong to active player! (use -f to circumvent limit)")
            return


    elif pos >= 40 and pos < 56: #Exit area
        index = (pos - 40) % 4
        area = (pos - 40) // 4
        mv.from_state_loc = area+1
        mv.from_index = index
        mv.from_count, mv.from_player = current_board.exit_states[area][index]
        mv.to_index = index + roll
        mv.to_state_loc = mv.from_state_loc
        if mv.to_index < 4:
            mv.to_count, mv.to_player = current_board.exit_states[area][mv.to_index]
        elif mv.to_index == 4: #Exit move!
            mv.to_player = 0
            mv.to_count = 0
        if "f" not in flags and current_board.exit_states[area][mv.from_index][1] == 0:
            error_message("Invalid move - no piece in selected exit square")
            return
        if "f" not in flags and mv.from_player != current_board.active_player:
            error_message("Invalid move - piece does not belong to active player! (use -f to circumvent limit)")
            return

    elif pos == -1:
        mv.from_player = current_board.active_player
        mv.from_state_loc = -mv.from_player
        mv.to_state_loc = 0
        mv.to_index = (mv.from_player - 1) * 10 + roll - 1
        mv.to_count, mv.to_player = current_board.board_state[mv.to_index]
        if "f" not in flags and current_board.start_counts[mv.from_player-1] == 0:
            error_message("Invalid move - no piece in start area")
            return
        if "f" not in flags and (roll != 6 and roll != 1):
            error_message("Invalid move - must have 6 or 1 to move out from start area")
            return


    attrs = vars(mv)
    print(', '.join("%s: %s" % item for item in attrs.items()))

    current_board.move(mv)

    print("New roll:", current_board.roll)
    print("Active player:", current_board.active_player)

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

def cmd_pass(current_board, flags):
    #cmd pass
    current_board.progress_turn()
    print("Turn passed.")
    print("New roll:", current_board.roll)
    print("Active player:", current_board.active_player)

def error_message(reason):
    print("Command failure: " + reason + ". Please try again.")