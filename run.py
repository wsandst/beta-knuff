import graphics
from board import Board

def main():
    board = Board()
    board.board_state = list(range(40))
    board.print_data()
    graphics.display_board(board)
    input()
    
if __name__ == "__main__":
    main()