from player import *

class NeatPlayer(Player):
    def __init__(self, name = "Unspecified", net = None):
        self.name = name
        self.win_count = [0,0,0,0]
        self.has_won = False
        self.net = net

    def play(self, current_board, moves):
        """ Run min-max on all generated moves """
        self.exit_squares = [40, 10, 20, 30]

        self.player = current_board.active_player

        best_index = 0
        best_score = -1000000
        self.nodes = 0

        for i, mv in enumerate(moves):
            current_board.move(mv)
            score = self.net.activate(current_board.generate_compact_repr_hot())[0]
            current_board.unmove(mv)

            if score > best_score:
                best_score = score
                best_index = i

        return moves[best_index]