"""Command functions and helpers"""

import board, graphics, move, player
import copy, random, time, multiprocessing
import cProfile
import config
if config.ENABLE_ML_PLAYER:
    import ml_model
    import players.ml_player

from players import neat_player

import export
import neat


board_eval_exporter = export.BoardEvalExporter()

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
play <player1/2/3/4> [player2/3/4] [player3/4] [player4] [-nm] [-d] [-c count] [-p playercount] [-m]
play: Plays the game with the selected players. -mn for manual input between turns, -d to display board every turn, -r to reset the board between games, 
-c to repeat game count times. -o removes all extra checks, will break other flags, -p specifies how many players. 
-nm for disabling multithreading
Players available: random, randomtake, rulebased, human, empty (no player)
Machine learning related:

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
        roll = try_convert_to_int(flags["f"])
        if roll is None:
            return
        current_board.roll = int(flags["f"])
    print("Roll: {}".format(current_board.roll))

def cmd_turn(current_board : board.Board, flags : dict):
    """cmd: turn [-f turn]. Display the current turn or force it to a certain turn with -f"""
    if "f" in flags:
        turn = try_convert_to_int(flags["f"])
        if turn is None:
            return
        current_board.active_player = turn
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
    [-p playercount] [-swap] [-mt] [-ssm] [-mn] [-d] [-rank] [-e filename]
    
    Play cmd which simulates a game with the inputted player types. Flags:
    -c [count] runs multiple games in a row
    -p allows to specify how many players should play, up to 4. 
    -swap rotates the player starting positions between games to remove starting bias.
    -mt uses multithreading to improve performance
    -ssm makes single moves automatically for players, saving performance
    -d displays the board between every turn
    -rank keeps playing the games after the first player has won to get total rankings.
    -mn waits for manual input between turns.
    -g combines both -swap and -mt
    -e keeps track of board states and saves them to json
    """
    if "default" in flags and isinstance(flags["default"], str):
        flags["default"] = [flags["default"]]

    if "default" not in flags or len(flags["default"]) > 4:
        error_message("The required arguments are missing or are incorrectly formated")
        return

    if "g" in flags:
        flags["swap"] = None
        flags["mt"] = None
        
    players = get_player_classes(flags, player_dict)
    if players == None:
        error_message("The specified player types are invalid")
        return

    play_count = 1
    # Set the total player count based on flag -p
    current_board.player_count = 4
    if "p" in flags:
        player_count = try_convert_to_int(flags["p"])
        if player_count is None:
            return
        current_board.player_count = player_count

    # Set game count based on flag -c
    if "c" in flags:
        play_count = try_convert_to_int(flags["c"])
        if play_count is None:
            return

    global result
    result = [0, 0, 0, 0]

    # Do multithreading with flag mt
    if "mt" not in flags:
        board_list = [current_board]
        players_list = [players]
        play_games(current_board, flags, players, play_count, 1)
        result = [players[0].win_count[0], players[1].win_count[0], players[2].win_count[0], players[3].win_count[0]]
    else:
        def report_res(res):
            global result
            result = [result[i] + res[i] for i in range(len(res))]

        thread_count = multiprocessing.cpu_count()
        thread_play_count = play_count // thread_count
        players_list = [copy.deepcopy(players) for i in range(thread_count)]
        board_list = [copy.deepcopy(current_board) for i in range(thread_count)]
        tpool = multiprocessing.Pool(processes=thread_count)
        for i in range(thread_count):
            board_list[i].roll_dice()
            tpool.apply_async(play_games, args=(board_list[i], flags, players_list[i], thread_play_count, i), callback=report_res)
            #play_games(board_list[i], flags, players_list[i], thread_play_count)
        report_res(play_games(copy.deepcopy(current_board), flags, copy.deepcopy(players), play_count - thread_play_count * thread_count, -1))
        while sum(result) != play_count:
            time.sleep(0.5)
    for player_count, player in enumerate(players, 1):
        if player_count > current_board.player_count:
            break
        print("Player {}: {} wins ({})\t{}".format(player_count, result[player_count - 1], player.name, sum(result)))   

    if 'e' in flags:
        board_eval_exporter.save(flags['e'])  
    """
    for player_count, player in enumerate(players, 1):
        if player_count > current_board.player_count:
            break
        print("Player {}: {} wins ({})\t{}".format(player_count, win_counts[player_count-1][0], player.name, win_counts[player_count-1]))

    #print("Average ply: {} (total {}, max {}, min {})".format(total_ply / play_count, total_ply, max_ply, min_ply))"""

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
    skip_single_moves = "ssm" in flags
    place = 0

    start = time.time()
    last_update = time.time()

    original_players = players.copy()
    last_update = -1
    update_index = 2
    next_update_num = (update_index * play_count) // 10
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

            if "e" in flags:
                current_player = players[current_board.active_player-1]
                board_eval_exporter.track_score(current_board, current_player)

            if "mn" in flags:
                if input() == "exit":
                    return
            if skip_single_moves and len(moves) == 1:
                current_board.move(moves[0])
            elif len(moves) > 0:
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
        if c == next_update_num:
            #last_update = time.time()
            print(f"Completed {10 * update_index} percent of task (thread {thread_num})")
            update_index += 2
            next_update_num = (update_index * play_count) // 10

    end = time.time()
    print("Thread {} execution finished after time: {} s".format(thread_num, round(end - start, 4)))
    return [original_players[i].win_count[0] for i in range(4)] 

def cmd_perft(current_board: board.Board, flags : dict):
    """cmd: perft <depth>. Generates a tree of all valid moves with all valid rolls and counts
    leaf nodes"""
    depth_in = try_convert_to_int(flags["default"])
    if depth_in is None:
        return
    random.seed(1)
    work_board = copy.deepcopy(board)
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

    nodes = testPerf(work_board, depth_in)
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

def cmd_ml_generate_data(current_board: board.Board, flags : dict):
    """ cmd generate_data <gamecount>: generate board->evaluation data for ML 
    
    Uses the GenerateDataPlayer to play a bunch of games against random,
    and saves the data to a file in the end.
    """
    play_count = 0
    filename = "data"
    if "default" not in flags:
        error_message("Incorrectly formatted arguments")
        return
    if isinstance(flags["default"], str):
        play_count = int(flags["default"])
    else:
        play_count = int(flags["default"][0])
        filename = flags["default"][1]

    print("Generating input/output data using GenDataPlayer and x3 RandomPlayer games")

    gendata_player = ml_player.GenerateDataPlayer()
    players = [gendata_player, player.RandomPlayer(), player.RandomPlayer(), player.RandomPlayer()]

    new_flags = {}#{"swap": None}

    play_games(current_board, new_flags, players, play_count, 0)

    gendata_player.save_data_to_file(f"models/{filename}")
    print(f"Data generation complete and saved to models/{filename}_inputs.txt and models/{filename}_outputs.txt.")

def cmd_ml_train(current_board : board.Board, flags):
    """ cmd train [filename] : train the machine learning model on a data file ("data" is default) """
    filename = "data"
    if "default" in flags and isinstance(flags["default"], str):
        filename = flags["default"]

    print("Training ML Model on saved input/output data")
    
    ml_player1 = ml_player.MLPlayer("MLPlayer")
    ml_player1.model.train(filename)

    print("Model trained.")

def cmd_ml_load_model(current_board : board.Board, flags, player_dict):
    """ cmd loadmodel <filename> : load a machine learning model from file into MLPlayer """
    if "default" not in flags:
        error_message("Incorrectly formatted arguments")
        return
    model_name = flags["default"]
    try:
        player_dict["ml"] = lambda: ml_player.MLPlayer("MachineLearning", model_name)
        player_dict["machinelearning"] = lambda: ml_player.MLPlayer("MachineLearning", model_name)
        player_dict["nn"] = lambda: ml_player.MLPlayer("MachineLearning", model_name)
    except:
        error_message("The specified ML model does not exist")
        return
    
    print(f"Loaded model {model_name} into MLPlayer")


def cmd_neat_train(current_board: board.Board, flags : dict):
    """ cmd neattrain [filename] : train the machine learning model on a data file ("data" is default) """
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         "src/neat/feedfoward.conf")

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(lambda genomes, config: neat_eval_genomes(current_board, 1000, genomes, config), 300)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    evol_player = neat_player.NeatPlayer("Neat", winner_net)
    players = [evol_player, player.RandomPlayer(), player.RandomPlayer(), player.RandomPlayer()]
    wins = play_games(current_board, {}, players, 1000, 0)
    win_percentage = wins[0] / 1000
    print(f"Win percentage: {win_percentage}%",)


    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')

def neat_eval_genomes(current_board, play_count, genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        evol_player = neat_player.NeatPlayer("Neat", net)
        players = [evol_player, player.RandomPlayer(), player.RandomPlayer(), player.RandomPlayer()]

        new_flags = {"swap": None}
        wins = play_games(current_board, new_flags, players, play_count, 0)
        win_percentage = (wins[0] / play_count)
        genome.fitness = (win_percentage - 0.25) ** 2
        print(f"Genome: {genome_id}, fitness: {genome.fitness}, win percentage: {win_percentage*100}%")

def cmd_neat_load_model(current_board, flags: dict, player_dict):
    """ cmd neatloadmodel <filename> : load an evolutinary NEAT learning model from file into MLPlayer """
    pass

def error_message(reason):
    """Support function for logging error messages related to functions"""
    print("Command failure: {}. Please try again.".format(reason))

def try_convert_to_int(num):
    """ Return a string as an integer, or none if the conversion is not possible 
        Used for error checking
    """
    if num.isdigit():
        return int(num)
    else:
        error_message("Failed to convert argument to integer")
        return None