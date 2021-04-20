"""Main file with command loop"""

import config
from board import Board
import player
import mct_player
if config.ENABLE_ML_PLAYER:
    import ml_player

from commands import *
from typing import Union

init_message = """---------------------------
BetaKnuff Development Build
---------------------------

Type 'help' for a list of commands.
"""

#Dictionaries for mapping commands/playertypes to functions/classes
commands = {}
players = {}

def add_command(triggers : Union[dict, str], function):
    """Add a command to the global players dictionary"""
    if isinstance(triggers, str):
        commands[triggers] = function
    else:
        for trigger in triggers:
            commands[trigger] = function

def add_player(names : Union[dict, str], function):
    """Add a player type to the global players dictionary"""
    if isinstance(names, str):
        players[names] = function
    else:
        for trigger in names:
            players[trigger] = function


def parse(input_list : list) -> dict:
    """Parse the flags of a written line into dictionary representing the flags

    The outputted dict is in the form of {FLAG:value, ...}, where value is
    Union[str, int, list]. Note that the preceeding '-' is removed from flag dict key. 
    The default arguments (with no flag, connecting directly to the command) are stored under
    the flag 'default'
    """
    flags = {}
    if len(input_list) > 1:
        i = 1
        while i < len(input_list) and not (input_list[i][0] == '-' and input_list[i][1].isalpha()):
            flags.setdefault("default", [])
            flags["default"].append(input_list[i])
            i += 1
        flag = ''
        for value in input_list[i:]:
            if value[0] == '-':
                flag = value[1:]
                flags[flag] = []
            else:
                flags[flag].append(value)

    for flag, args in flags.items():
        if len(args) == 0: 
            flags[flag] = None
        elif len(args) == 1: 
            flags[flag] = args[0]

    return flags
    

def main():
    """Main function containing the command input loop"""
    main_board = Board()

    flags = {}

    # Registring the command strings and corresponding function
    add_command(["help", "h"], lambda: cmd_help(flags))
    add_command(["exit", "quit", "q"], lambda: cmd_exit(flags))
    add_command(["display", "disp", "d"], lambda: cmd_display(main_board, flags))
    add_command("reset", lambda: cmd_reset(main_board, flags))
    add_command("roll", lambda: cmd_roll(main_board, flags))
    add_command("set", lambda: cmd_set(main_board, flags))
    add_command(["move", "mv"], lambda: cmd_move(main_board, flags))
    add_command(["pass", "skip"], lambda: cmd_pass(main_board, flags))
    add_command(["moves", "mvs"], lambda: cmd_moves(main_board, flags))
    add_command(["play", "run", "p"], lambda: cmd_play(main_board, flags, players))
    #add_command("performance", lambda: cmd_performance_test(main_board, flags))
    add_command("perft", lambda: cmd_perft(main_board, flags))
    add_command("rules", lambda: cmd_rules(main_board, flags))
    add_command("eval", lambda: cmd_eval(main_board, flags))
    if config.ENABLE_ML_PLAYER:
        add_command(["generatedata", "gendata", "gd"], lambda: cmd_ml_generate_data(main_board, flags))

    # Registering player types and their corresponding classes
    add_player(["random", "rand", "r"], lambda: player.RandomPlayer("Random"))
    add_player(["randomtake", "randtake", "rt", "rtake"], lambda: player.RandomTakePlayer("RandomTake"))
    add_player(["rulebased", "rb", "ruleb"], lambda: player.RuleBasedPlayer("RuleBased"))
    add_player(["human", "h", "manual"], lambda: player.HumanPlayer("Human"))
    add_player(["empty", "none", "e", "n"], lambda: player.EmptyPlayer("None"))
    add_player(["minmax", "mm"], lambda: player.MinMaxPlayer("MinMax"))
    add_player(["montecarlo", "mc"], lambda: mct_player.MontePlayer("MonteCarlo"))
    if config.ENABLE_ML_PLAYER:
        add_player(["genmachinelearning", "gml", "gendata"], lambda: ml_player.GenerateDataPlayer("GenerateDataPlayer"))
        add_player(["machinelearning", "ml", "nn"], lambda: ml_player.MLPlayer("MachineLearning"))

    print(init_message)

    # Main input loop. Grab input, parse and execute command
    while True:
        input_list = input("\nbknuff: ").split()
        flags = parse(input_list)
        if len(input_list) > 0:
            command = input_list[0]
            if command in commands:
                commands[command]()
            else:
                print("The command was not recognized. Type 'help' for a list of commands")
        else:
            print("The command was not recognized. Type 'help' for a list of commands")