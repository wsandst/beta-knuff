from board import Board
from commands import *

init_message = """---------------------------
BetaKnuff Development Build
---------------------------

Type 'help' for a list of commands.

"""

commands = {}

def add_command(triggers, function):
    if isinstance(triggers, str):
        commands[triggers] = function
    else:
        for trigger in triggers:
            commands[trigger] = function


def parse(input_list):
    flags = {}
    if len(input_list) > 1:
        i = 1
        while input_list[i][0] != '-':
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
    add_command(["display", "disp", "d"], lambda: cmd_display(main_board, flags))
    add_command("reset", lambda: cmd_reset(main_board, flags))
    add_command("roll", lambda: cmd_roll(main_board, flags))

    print(init_message)

    while True:
        input_list = input("Bknuff: ").split()
        flags = parse(input_list)
        command = input_list[0]
        if command in commands:
            pass
            commands[command]()
        else:
            print("The command was not recognized. Type 'help' for a list of commands")