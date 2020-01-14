import move, board
import random

class Player: #Parent class to be inherited
    def play(self, current_board, moves):
        return move.Move()

class RandomPlayer(Player):
    #Randomly selects a move
    def play(self, current_board, moves):
        return random.choice(moves)
    
class RandomTakePlayer(Player):
    #Plays randomly except for when it can take a piece, which it then does
    def play(self, current_board, moves):
        for mv in moves:
            if mv.to_player != 0 and mv.to_player != mv.from_player: #Can take a piece, good move!
                return mv
        else:
            return random.choice(moves)

class RuleBasedPlayer(Player):
    #Plays with basic rules, tries to approximate a good human player
    def play(self, current_board, moves):
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

class HumanPlayer(Player):
    #Human player selects a move
    def play(self, current_board, moves):
        print("Human turn. Select a move from the move list: ")
        while True:
            move_count = input()
            if move_count.isdigit():
                return moves[int(move_count)-1]
            else:
                print("Not a valid move. Try again.")