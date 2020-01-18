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
    def eval_piece(self, distance):
        return 10 + distance

    def eval(self, current_board):
        score = 0

        last_piece_index = 0
        last_piece_count = 0
        for index, piece in enumerate(current_board.board_state):
            player = piece[1]
            if player != 0:
                distance_from_exit = current_board.distance_from_exit(player, index)
                if player == current_board.active_player: #Your own piece
                    score += self.eval_piece(distance_from_exit)
                else: #Another player
                    score -= self.eval_piece(distance_from_exit)

        for player, state in enumerate(current_board.exit_states, 1):
            for piece in state:
                if piece[1] != 0:
                    if player == current_board.active_player:
                        score += 60
                    else:
                        score -= 60

        for player, count in enumerate(current_board.exit_counts, 1):
            if player == current_board.active_player:
                score += 70*count
            else:
                score -= 70*count

        return score


        #Plays with basic rules, tries to approximate a good human player
    def play(self, current_board, moves):
        best_index = 0
        best_score = -1000000
        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board)
            current_board.unmove(mv)

            if score > best_score:
                best_score = score
                best_index = i

        return moves[best_index]
        
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