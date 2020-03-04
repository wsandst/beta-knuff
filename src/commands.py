"""Command functions and helpers"""

import board, graphics, move, player
import copy, random, time
import cProfile

#List of commands
command_list = """List of commands for BetaKnuff Development Build:
exit                                Exit BetaKnuff
help                                Lists commands for BetaKnuff
display [-a]                        Displays the current game board and state. -a prints additional info
reset                               Resets the main board to start
roll [-f num]                       Display the roll for this turn. -f forces a reroll to specified number
rules [name] [option]               Prints the current rules. Specify name to set the corresponding rule config to true/false or a number.
move <movenum>                      Move the move number from cmd moves. pass to skip.
moves [player] [roll]               Lists valid moves this turn
pass                                Skips this players turn. Used when no moves are available
set <pos> <player> [count]          Add a piece on the board, with no regards to the game rules
performance <depth>                 Generates a tree of valid moves, simulating one roll
perft <depth>                       Generates a tree of valid moves, simulating all rolls
play <player1/2/3/4> [player2/3/4] [player3/4] [player4] [-m] [-d] [-c count] [-p playercount] [-m]
play: Plays the game with the selected players. -mn for manual input between turns, -d to display board every turn, -r to reset the board between games, 
-c to repeat game count times. -o removes all extra checks, will break other flags, -p specifies how many players. 
-m for multithreading multiple games
Players available: random, randomtake, rulebased, human, empty (no player)
"""

#This module adds commands for the command parser in main
#Flags is a dictionary containing the char flag (ex 'd') and the corresponding arg (None if none)
#The "standard" arguments, ie the ones at the start without a flag is filed under the flag "-default" 

def cmd_display(current_board : board.Board, flags : dict):
    """cmd: display [-a]. Display the board state. -a for more information"""
    graphics.display_board(current_board)
    if 'a' in flags:
        current_board.print_data()
    if 'p' in flags:
        current_board.print_active_pieces()

def cmd_reset(current_board : board.Board, flags : dict):
    """cmd: reset. Reset the board state to ready it for a new game"""
    current_board.board_state = copy.deepcopy(board.starting_board_state)
    current_board.exit_states = copy.deepcopy(board.starting_exit_states)
    current_board.start_counts = copy.deepcopy(board.starting_start_counts)
    current_board.exit_counts = copy.deepcopy(board.starting_exit_counts) 
    current_board.active_player = 1
    current_board.ply_count = 1
    current_board.roll_dice()
    current_board.roll_list = [current_board.roll]

def cmd_roll(current_board : board.Board, flags : dict):
    """cmd roll [-f roll]. Display the current roll. Force it to a specific roll with -f"""
    if "f" in flags:
        current_board.roll = int(flags["f"])
    print("Roll: {}".format(current_board.roll))

def cmd_turn(current_board : board.Board, flags : dict):
    """cmd: turn [-f turn]. Display the current turn or force it to a certain turn with -f"""
    if "f" in flags:
        current_board.active_player = int(flags["f"])
    print("Turn: {}".format(current_board.active_player))

def cmd_help(flags : dict):
    """cmd: help. Print the help string, containing command descriptions"""
    print(command_list)

def cmd_exit(flags : dict):
    """cmd: exit. Exit the program"""
    print("Exiting BetaKnuff...")
    exit()

def cmd_move(current_board : board.Board, flags : dict):
    """cmd: move <movecount>. Perform a move in the generated movelist, using movecount for index"""
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

def cmd_moves(current_board : board.Board, flags : dict):
    """cmd: moves. Prints available moves for the current player"""
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
    for i, mv in enumerate(moves):
        attrs = vars(mv)
        print("Move " + str(i) + ":", ', '.join("%s: %s" % item for item in attrs.items()))

def cmd_set(current_board : board.Board, flags : dict):
    """cmd: set <state> <index> <player> [count]. Set the index in state to player and optional count"""
    if "default" not in flags or len(flags["default"]) < 3:
        error_message("The required arguments are missing or are incorrectly formated")
        return

    state = int(flags["default"][0])
    pos = int(flags["default"][1])
    player = int(flags["default"][2])
    count = 1
    
    if len(flags["default"]) > 3:
        count = int(flags["default"][2])

    if state == -1:
        current_board.start_counts[player-1] = count
    elif state == 0:
        if pos < 40 and pos >= 0:
            current_board.board_state[pos] = (count, player)
    elif state > 0 and pos >= 0 and pos <= 4:
        current_board.exit_states[state-1][pos] = (count, player)
    else:
        error_message("The required arguments are incorrectly formated")

def cmd_pass(current_board : board.Board, flags : dict):
    """cmd: pass. Pass current turn"""
    current_board.progress_turn()
    print("Turn passed.")
    print("New roll:", current_board.roll)
    print("Active player:", current_board.active_player)

def get_player_classes(flags : dict, player_dict : dict):
    """Helper class for cmd play. Returns the classes representing the players based
    on the inputted player flags
    """
    arg_count = len(flags["default"]) 
    players = [0]*4
    if arg_count == 1:
        players = (flags["default"]*4).copy()
    elif arg_count == 2:
        players[0] = flags["default"][0]
        players[1:4] = [flags["default"][1] for i in range(3)]
    elif arg_count == 3:
        players[0] = flags["default"][0]
        players[1] = flags["default"][1]
        players[2:4] = [flags["default"][2] for i in range(2)]
    elif arg_count == 4:
        players = flags["default"].copy()
    try:
        players = [player_dict[i]() for i in players]
    except:
        return None

    return players

def cmd_play(current_board: board.Board, flags : dict, player_dict : dict):
    """cmd: play <player1> <player2/3/4> [player3/4] [player4] [-c count] [-o]
    [-p playercount] [-swap] 
    
    Play cmd which simulates a game with the inputted player types. Supports running multiple
    games in a row with flag -c. -p allows to specify how many players should play, up to 4. -swap
    rotates the player starting positions between games to remove starting bias.
    -rank keeps playing the games after the first player has won to get total rankings.
    -m waits for manual input between turns.
    """
    if "default" in flags and isinstance(flags["default"], str):
        flags["default"] = [flags["default"]]

    if "default" not in flags or len(flags["default"]) > 4:
        error_message("The required arguments are missing or are incorrectly formated")
        return
        
    players = get_player_classes(flags, player_dict)
    if players == None:
        error_message("The specified player types are invalid")
        return

    play_count = 1
    # Set the total player count based on flag -p
    current_board.player_count = 4
    if "p" in flags:
        current_board.player_count = int(flags["p"])

    # Set game count based on flag -c
    if "c" in flags:
        play_count = int(flags["c"])

    # Do multithreading on flag -m
    if "m" in flags:
        thread_count = 4
        thread_play_count = play_count // thread_count
        board_list = [copy.deepcopy(current_board) for i in range(thread_count)]
        players_list = [copy.deepcopy(players) for i in range(thread_count)] 
        for i in range(thread_count):
            board_list[i].roll_dice()
            play_games(board_list[i], flags, players_list[i], thread_play_count, i+1)
    else:
        board_list = [current_board]
        players_list = [players]
        play_games(current_board, flags, players, play_count, 1)

    # Game simulation finished. Now print various data related to the games
    # Combine win counts from the different threads for final output
    win_counts = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for players in players_list:
        for player_num, player in enumerate(players):
             win_counts[player_num] = [x + y for x, y in zip(win_counts[player_num], player.win_count)]
    for player_count, player in enumerate(players, 1):
        if player_count > current_board.player_count:
            break
        print("Player {}: {} wins ({})\t{}".format(player_count, win_counts[player_count-1][0], player.name, win_counts[player_count-1]))

    #print("Average ply: {} (total {}, max {}, min {})".format(total_ply / play_count, total_ply, max_ply, min_ply))

def play_games(current_board: board.Board, flags : dict, players, play_count: int, thread_num : int):
    """ Simulates play_count x games based on input from cmd play"""
    end = False

    total_ply = 0
    max_ply = 0
    min_ply = 1000
    moves = []
    doubleentry = [0,0,0,0]

    swap = "swap" in flags
    rankings = "rank" in flags
    place = 0

    start = time.time()
    last_update = time.time()

    # Loop for every game count
    # Loop, increment turn count, present moves to player classes and allow them to select
    for c in range(play_count):
        if swap:
            # Rotate the player start positions
            if current_board.player_count == 2:
                players[0], players[1] = players[1], players[0]
            elif current_board.player_count == 3:
                players[0], players[1], players[2] = players[1], players[2], players[0]
            elif current_board.player_count == 4:
                players[0], players[1], players[2], players[3] = players[1], players[2], players[3], players[0]

        while end is False:
            moves = current_board.generate_moves()
            if "d" in flags:
                cmd_display(current_board, flags)
                print("{} Legal moves for Player {} with Roll {}".format(len(moves), current_board.active_player, current_board.roll))
                for count, mv in enumerate(moves):
                    attrs = vars(mv)
                    print(count+1, ', '.join("%s: %s" % item for item in attrs.items()))

            if "mn" in flags:
                if input() == "exit":
                    return

            if len(moves) > 0:
                mv = players[current_board.active_player-1].play(current_board, moves)
                if mv == None: #Player decides to skip turn
                    current_board.progress_turn()
                    continue
                if mv.from_state_loc < 0 and mv.from_count == 2: #Double entry performed
                    doubleentry[current_board.active_player-1] += 1
                current_board.move(mv)
            else:
                current_board.progress_turn()

            for player, count in enumerate(current_board.exit_counts, 1):
                if count >= 4 and not players[player-1].has_won:
                    players[player-1].has_won = True
                    players[player-1].win_count[place] += 1
                    if rankings:
                        place += 1
                    else:
                        end = True

            if rankings:
                end = players[0].has_won and players[1].has_won and players[2].has_won and players[3].has_won


        total_ply += current_board.ply_count
        if max_ply < current_board.ply_count:
            max_ply = current_board.ply_count
        if min_ply > current_board.ply_count:
            min_ply = current_board.ply_count
        cmd_reset(current_board, flags)
        players[0].has_won, players[1].has_won, players[2].has_won, players[3].has_won = False, False, False, False
        end = False
        place = 0
        if time.time() - last_update > 1:
            last_update = time.time()
            print("Completed {} percent of task".format(round((c / play_count) * 100)))

    end = time.time()
    print("Thread {} execution finished after time: {} s".format(thread_num, round(end - start, 4)))

def cmd_perft(current_board: board.Board, flags : dict):
    """cmd: perft <depth>. Generates a tree of all valid moves with all valid rolls and counts
    leaf nodes"""
    depth_in = int(flags["default"])
    random.seed(1)
    workBoard = copy.deepcopy(board)
    def testPerf(board, depth):
        if depth <= 0:
            return 1
        numMoves = 0
        for r in range(6):
            board.roll = r
            moves = board.generate_moves()
            for move in moves:
                board.move(move)
                numMoves += testPerf(board, depth - 1)
                board.unmove(move)
            if len(moves) == 0:
                board.progress_turn()
                numMoves += testPerf(board, depth - 1)
                board.unprogress_turn()
        return numMoves


    start = time.perf_counter()

    nodes = testPerf(workBoard, depth_in)
    end = time.perf_counter()
    print("Searched: {} leaf nodes".format(nodes))
    print("Time taken: {} seconds ".format(round(end - start, 2)))
    print("Performed {} leaf nodes per second".format(round(nodes/(end - start))))

def cmd_eval(current_board: board.Board, flags : dict):
    """cmd eval: Evaluate the current position with RuleBasedPlayer-evaluation"""
    test_player = player.RuleBasedPlayer()
    test_player.exit_squares = [40, 10, 20, 30]
    print("Score:", test_player.eval(current_board, 1))

def cmd_rules(current_board: board.Board, flags : dict):
    """cmd rules <rule> <state>: change game rule <rule> to <state>
    
    Available rules: 
    New roll on six [reroll] on/off
    Double entry on first position with roll 6 [doubleentry] on/off
    """
    rule_option_dict = {"true": True, "on": True, "t": True, "false": False, "off": False, "f": False}

    if "default" in flags:
        try:
            name = flags["default"][0]
            setting = False
            if flags["default"][1].isdigit():
                setting = int(flags["default"][1]) 
            else:
                setting = rule_option_dict[str.lower(flags["default"][1])]
            if name == "reroll" or name == "new_roll_on_six" or name == "newroll" or name == "newrollonsix":
                current_board.rule_new_roll_on_six = setting
            elif name == "doubleentry" or name == "double_entry_on_six" or name == "doubleentryonsix":
                current_board.rule_double_entry_on_six = setting
        except:
            error_message("Incorrectly formatted arguments")
            return

    print("Rules:")
    print("Double entry from start allowed on roll 6:", current_board.rule_double_entry_on_six)
    print("New roll allowed after roll 6:", current_board.rule_new_roll_on_six)

def error_message(reason):
    """Support function for logging error messages related to functions"""
    print("Command failure: {}. Please try again.".format(reason))