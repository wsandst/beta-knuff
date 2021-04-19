"""Various Player classes which are used in cmd play and inherit from Player"""

import move, board
import random

class Player:
    """Parent class to be inherited for Players. Defines two needed functions: play and __init__"""
    def __init__(self, name = "Unspecified"):
        self.name = name
        self.win_count = [0,0,0,0]
        self.has_won = False

    def play(self, current_board, moves):
        return move.Move()

class RandomPlayer(Player):
    """ Randomly selects a move """
    def play(self, current_board, moves):
        return random.choice(moves)
    
class RandomTakePlayer(Player):
    """ Plays randomly except for when it can take a piece, which it then does """
    def play(self, current_board, moves):
        for mv in moves:
            if mv.to_player != 0 and mv.to_player != mv.from_player: #Can take a piece, good move!
                return mv
        else:
            return random.choice(moves)

class RuleBasedPlayer(Player):
    """Rulebased player using a simple eval function. 
    
    Tries to move pieces forward, take other pieces, enter the exit and 
    keep pieces away from taking distance
    """
    def eval_piece(self, distance: int, count = 1) -> int:
        """ Return the value of a piece at this square """
        return (10 + 39 - distance) * count
        #return (10 + distance) * count


    def eval_threats(self, current_board: board.Board, index: int, player: int) -> int:
        """Measures how many pieces are within taking range of this piece, 
        and gives 1/6 of their piece values"""
        score = 0
        exit_square = self.exit_squares[player-1]
        for i in range(6):
            index2 = (index + i) % 40
            if index2 == exit_square:
                break
            count2, player2 = current_board.board_state[index2]
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score += self.eval_piece(distance, count2)//6
        return score


    def eval(self, current_board, player_num):
        """Evaluate the current position by analyzing the board state with rule-based logic"""
        score = 0
   
        #Go through the main state and give points based on distance from the exit area
        for index, piece in enumerate(current_board.board_state):
            player = piece[1]
            if player != 0:
                distance_from_exit = current_board.distance_from_exit(player, index)
                count = piece[0]
                if player == player_num: #Your own piece
                    score += self.eval_piece(distance_from_exit, count)
                    score += self.eval_threats(current_board, index, player)
                else: #Another player
                    score -= self.eval_piece(distance_from_exit, count)
                    score -= self.eval_threats(current_board, index, player)
        
        #Give 60 points for every piece in the exit state
        for player, state in enumerate(current_board.exit_states, 1):
            for piece in state:
                if piece[1] != 0:
                    count = piece[0]
                    if player == player_num:
                        score += 60 * count
                    else:
                        score -= 60 * count

        # Give 70 points for every piece that has exited
        for player, count in enumerate(current_board.exit_counts, 1):
            if player == player_num:
                score += 70*count
            else:
                score -= 70*count

        # Adjust how many pieces are optimal on the board concurrently
        #piece_count_active = 4 - (current_board.start_counts[player_num-1] + current_board.exit_counts[player_num-1])
        #piece_count_values = [-100,0,0, -100, -200]
        #score += piece_count_values[piece_count_active]
 
        return score

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board, self.player)
            current_board.unmove(mv)

            if score >= best_score:
                best_score = score
                best_index = i

        return moves[best_index]
      
class RuleBasedPlayer2(Player):
    """Rulebased player using a simple eval function. 
    
    Tries to move pieces forward, take other pieces, enter the exit and 
    keep pieces away from taking distance
    """
    def eval_piece(self, distance: int, count = 1) -> int:
        """ Return the value of a piece at this square """
        return (10 + 39 - distance) * count
        #return (10 + distance) * count


    def eval_threats(self, current_board: board.Board, index: int, player: int) -> int:
        """Measures how many pieces are within taking range of this piece, 
        and gives 1/6 of their piece values"""
        score = 0
        exit_square = self.exit_squares[player-1]
        distance = current_board.distance_from_exit(player, index)
        count, _dummy = current_board.board_state[index]
        this_piece_value = self.eval_piece(distance, count)
        for i in range(1, 7):
            index2 = (index + i) % 40
            if index2 == exit_square:
                break
            count2, player2 = current_board.board_state[index2] #in front
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score += self.eval_piece(distance, count2)//6
            index2 = (index - i) % 40
            count2, player2 = current_board.board_state[index2] #behind
            if player2 != 0 and player2 != player: #Is opponent piece
                distance = current_board.distance_from_exit(player2, index2)
                score -= this_piece_value // 6
        return score


    def eval(self, current_board, player_num):
        """Evaluate the current position by analyzing the board state with rule-based logic"""
        score = 0
   
        #Go through the main state and give points based on distance from the exit area
        for index, piece in enumerate(current_board.board_state):
            player = piece[1]
            if player != 0:
                distance_from_exit = current_board.distance_from_exit(player, index)
                count = piece[0]
                if player == player_num: #Your own piece
                    score += self.eval_piece(distance_from_exit, count)
                    score += self.eval_threats(current_board, index, player)
                else: #Another player
                    score -= self.eval_piece(distance_from_exit, count)
                    #score -= self.eval_threats(current_board, index, player)
        
        #Give 60 points for every piece in the exit state
        for player, state in enumerate(current_board.exit_states, 1):
            for piece in state:
                if piece[1] != 0:
                    count = piece[0]
                    if player == player_num:
                        score += 60 * count
                    else:
                        score -= 60 * count

        # Give 70 points for every piece that has exited
        for player, count in enumerate(current_board.exit_counts, 1):
            if player == player_num:
                score += 70*count
            else:
                score -= 70*count

        # Adjust how many pieces are optimal on the board concurrently
        #piece_count_active = 4 - (current_board.start_counts[player_num-1] + current_board.exit_counts[player_num-1])
        #piece_count_values = [-100,0,0, -100, -200]
        #score += piece_count_values[piece_count_active]
 
        return score

    def play(self, current_board, moves):
        """ Evaluate all the moves and pick the one with the highest eval score"""
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.eval(current_board, self.player)
            current_board.unmove(mv)

            if score >= best_score:
                best_score = score
                best_index = i

        return moves[best_index]
      

class MinMaxPlayer(RuleBasedPlayer):
    """ Min max player which performs a tree search and uses the eval function from RuleBased"""
    def minmax(self, current_board, depth):
        """ Min max search tree, which takes chance into account """
        if depth <= 0:
            return self.eval(current_board, self.player)

        sum_score = 0
        old_roll = current_board.roll
        if current_board.active_player == self.player:
            optimizer = max
            start_val = -1000000
        else:
            start_val = 1000000
            optimizer = min
            
        for roll in range(6):
            current_board.roll = roll + 1
            value = start_val
            moves = current_board.generate_moves()
            if len(moves) == 0:
                value = optimizer(0, value)
            for mv in moves:
                current_board.move(mv)
                value = optimizer(self.minmax(current_board, depth-1), value)
                current_board.unmove(mv)
            sum_score += value

        current_board.roll = old_roll
        return sum_score


    def play(self, current_board, moves):
        """ Run min-max on all generated moves """
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000
        self.nodes = 0

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.minmax(current_board, 4)
            current_board.unmove(mv)

            if score > best_score:
                best_score = score
                best_index = i

        return moves[best_index]

class HumanPlayer(Player):
    """ Human player, selects move manually"""
    def play(self, current_board, moves):
        print("Human turn. Select a move from the move list: ")
        while True:
            move_count = input()
            if move_count.isdigit():
                return moves[int(move_count)-1]
            else:
                print("Not a valid move. Try again.")

class EmptyPlayer(Player): 
    """ Empty player, trick to skip a player on the board. Useful to only play 1,3 etc"""
    def play(self, current_board, moves):
        return None