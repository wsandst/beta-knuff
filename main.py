from board import Board
import player
from commands import *

init_message = """---------------------------
BetaKnuff Development Build
---------------------------

Type 'help' for a list of commands.

"""

commands = {}
players = {}

def add_command(triggers, function):
    if isinstance(triggers, str):
        commands[triggers] = function
    else:
        for trigger in triggers:
            commands[trigger] = function

def add_player(names, function):
    if isinstance(names, str):
        players[names] = function
    else:
        for trigger in names:
            players[trigger] = function


def parse(input_list):
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
                flag = value[1]
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
    main_board = Board()

    flags = {}

    add_command(["help", "h"], lambda: cmd_help(flags))
    add_command("exit", lambda: cmd_exit(flags))
    add_command(["display", "disp", "d"], lambda: cmd_display(main_board, flags))
    add_command("reset", lambda: cmd_reset(main_board, flags))
    add_command("roll", lambda: cmd_roll(main_board, flags))
    add_command("set", lambda: cmd_set(main_board, flags))
    add_command(["move", "mv"], lambda: cmd_move(main_board, flags))
    add_command(["pass", "skip"], lambda: cmd_pass(main_board, flags))
    add_command(["moves", "mvs"], lambda: cmd_moves(main_board, flags))
    add_command(["play", "run", "p"], lambda: cmd_play(main_board, flags, players))
    add_command("performance", lambda: cmd_performance_test(main_board, flags))
    add_command("perft", lambda: cmd_perft(main_board, flags))

    add_player(["random", "rand", "r"], lambda: player.RandomPlayer("Random"))
    add_player(["randomtake", "randtake", "rt", "rtake"], lambda: player.RandomTakePlayer("RandomTake"))
    add_player(["rulebased", "rb", "ruleb"], lambda: player.RuleBasedPlayer("RuleBased"))
    add_player(["human", "h", "manual"], lambda: player.HumanPlayer("Human"))
    add_player(["empty", "none", "e", "n"], lambda: player.EmptyPlayer("None"))

    print(init_message)

    while True:
        input_list = input("\nBknuff: ").split()
        flags = parse(input_list)
        if len(input_list) > 0:
            command = input_list[0]
            if command in commands:
                commands[command]()
            else:
                print("The command was not recognized. Type 'help' for a list of commands")
        else:
            print("The command was not recognized. Type 'help' for a list of commands")