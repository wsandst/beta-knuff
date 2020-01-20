import move, board
import random

class Player: #Parent class to be inherited
    def __init__(self, name = "Unspecified"):
        self.name = name

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
    #Rulebased player using a simple eval function. Tries to move pieces forward, take other pieces, enter the exit and keep pieces away from taking distance
    def eval_piece(self, distance, count = 1):
        return (10 + distance) * count

    def eval_threats(self, current_board, index, player):
        #Measures how many pieces are within taking range of this piece, and gives 1/6 of their piece values
        score = 0
        exit_square = self.exit_squares[current_board.active_player-1]
        for i in range(6):
            index2 = (index + i) % 40
            if index2 == exit_square:
                break
            count2, player2 = current_board.board_state[index2]
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score += self.eval_piece(distance, count2)//6
        return score


    def eval(self, current_board):
        score = 0

        for index, piece in enumerate(current_board.board_state):
            player = piece[1]
            if player != 0:
                distance_from_exit = current_board.distance_from_exit(player, index)
                count = piece[0]
                if player == current_board.active_player: #Your own piece
                    score += self.eval_piece(distance_from_exit) * count
                    score += self.eval_threats(current_board, index, player)
                else: #Another player
                    score -= self.eval_piece(distance_from_exit) * count
                    score -= self.eval_threats(current_board, index, player)

        for player, state in enumerate(current_board.exit_states, 1):
            for piece in state:
                if piece[1] != 0:
                    count = piece[0]
                    if player == current_board.active_player:
                        score += 60 * count
                    else:
                        score -= 60 * count

        for player, count in enumerate(current_board.exit_counts, 1):
            if player == current_board.active_player:
                score += 70*count
            else:
                score -= 70*count

        return score


        #Plays with basic rules, tries to approximate a good human player
    def play(self, current_board, moves):
        self.exit_squares = [40, 10, 20, 30]

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

class EmptyPlayer(Player): #Empty player, trick to skip a player on the board. Useful to only play 1,3 etc
    #Human player selects a move
    def play(self, current_board, moves):
        return None