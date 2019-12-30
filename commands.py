import board, graphics

#List of commands
command_list = """List of commands for BetaKnuff Development Build:
exit                        Exit BetaKnuff
display -a                  Displays the current game board and state. -e prints additional info
reset                       Resets the main board to start
roll                        Display the roll for this turn.
move    [pos] -d [distance] Move piece on pos with current roll. -d to override roll
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
    current_board = board.Board()

def cmd_roll(current_board, flags):
    #cmd: roll
    print("Roll: ", current_board.roll)

def cmd_help(flags):
    print(command_list)

def cmd_move(current_board, flags):
    pass