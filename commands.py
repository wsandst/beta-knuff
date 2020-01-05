import board, graphics, move
import copy, random

#List of commands
command_list = """List of commands for BetaKnuff Development Build:
exit                                Exit BetaKnuff
help                                Lists commands for BetaKnuff
display [-a]                        Displays the current game board and state. -e prints additional info
reset                               Resets the main board to start
roll [-f num]                       Display the roll for this turn. -f forces a reroll to specified number
move <movenum>                      Move the move number from cmd moves. pass to skip.
moves [player] [roll]               Lists valid moves this turn
pass                                Skips this players turn. Used when no moves are available
set <pos> <player> [count]          Add a piece on the board, with no regards to the game rules
selfplay [-m] [-d]                  Active selfplay. -m to add a manual input between every turn. -d to display the board every turn.
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
    current_board.exit_counts = copy.deepcopy(board.starting_exit_counts) 
    current_board.active_player = 1
    current_board.ply_count = 1
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
    elif flags["default"] == "pass":
        cmd_pass(current_board, flags)
        return
    
    moves = current_board.generate_moves()
    if len(moves) < int(flags["default"]):
        error_message("The move count is not in the move list")
        return

    mv = moves[int(flags["default"])-1]

    attrs = vars(mv)
    print("Made move:",', '.join("%s: %s" % item for item in attrs.items()))

    current_board.move(mv)

    print("New roll:", current_board.roll)
    print("Active player:", current_board.active_player)

def cmd_moves(current_board, flags):
    #cmd: moves
    player = None
    roll = None
    if "default" in flags:
        if len(flags["default"]) == 1:
            player = int(flags["default"][0])
        elif len(flags["default"] == 2):
            player = int(flags["default"][0])
            roll = int(flags["default"][1])
    else:
        moves = current_board.generate_moves(player, roll)
    


    print("Legal moves for Player", current_board.active_player, "with Roll", current_board.roll)
    i = 1
    for mv in moves:
        attrs = vars(mv)
        print("Move " + str(i) + ":", ', '.join("%s: %s" % item for item in attrs.items()))
        i += 1

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

def cmd_selfplay(current_board, flags):
    #cmd: selfplay
    #Plays randomly against itself
    win = False
    winning_player = 0
    winning_counts = [0,0,0,0]
    play_count = 1
    total_ply = 0
    max_ply = 0
    min_ply = 1000
    if "c" in flags:
        play_count = int(flags["c"])
    for c in range(play_count):
        while win is False:
            moves = current_board.generate_moves()
            if "d" in flags:
                cmd_display(current_board, flags)
                print(len(moves), "Legal moves for Player", current_board.active_player, "with Roll", current_board.roll)
                for mv in moves:
                    attrs = vars(mv)
                    print(', '.join("%s: %s" % item for item in attrs.items()))

            if "m" in flags:
                input()

            if len(moves) > 0:
                if current_board.active_player == 1:
                    mv = select_move_highiq(current_board, moves)
                    current_board.move(mv)
                #else:
                    #mv = random.choice(moves) #Pick a move
                    #current_board.move(mv)
                else:
                    mv = select_move_take(moves)
                    current_board.move(mv)
            else:
                current_board.progress_turn()
            i = 1
            for count in current_board.exit_counts:
                if count >= 4:
                    win = True
                    winning_player = i
                i += 1
        
        winning_counts[winning_player-1] += 1
        if "r" in flags:
            total_ply += current_board.ply_count
            if max_ply < current_board.ply_count:
                max_ply = current_board.ply_count
            if min_ply > current_board.ply_count:
                min_ply = current_board.ply_count
            cmd_reset(current_board, flags)
            win = False

        if c != 0 and c % 200 == 0:
            print("Completed", (c / play_count) * 100, "percent of task")
    i = 1
    for count in winning_counts:
        print("Player " + str(i) + ": " + str(count) + " wins")
        i += 1
    print("Average ply: {} (total {}, max {}, min {})".format(total_ply / play_count, total_ply, max_ply, min_ply))
    

def error_message(reason):
    print("Command failure: " + reason + ". Please try again.")

def select_move_take(moves):
    for mv in moves:
        if mv.to_player != 0 and mv.to_player != mv.from_player: #Can take a piece, good move!
            return mv
    else:
        return random.choice(moves)

def select_move_highiq(current_board, moves):
    for mv in moves: #Take if possible
        if mv.to_player != 0 and mv.to_player != mv.from_player: #Can take a piece, good move!
            return mv
    #Keep pieces on main board to x if possible:
    if current_board.roll == 1 or current_board.roll == 6 and (4 - (current_board.exit_counts[current_board.active_player-1] + current_board.start_counts[current_board.active_player-1])) < 2:
        for mv in moves:
            if mv.from_state_loc > 0:
                return mv
    
    #Move in pieces you can
    for mv in moves:
        if mv.to_index == 4:
            return mv
    return random.choice(moves)