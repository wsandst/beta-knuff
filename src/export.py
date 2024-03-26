import copy
import json
from player import RuleBasedPlayer, NormRuleBasedPlayer, MinMaxPlayer
import re

# Map board state to evaluation:

class BoardEvalExporter:
    def __init__(self):
        self.state = []

    def save(self, filename):
        """ Save board evaluations to json file """
        json_str = json.dumps(self.state, indent=4)
        json_str = re.sub(r'(?<=[0-9],)\s+(?=[0-9])', ' ', json_str)
        json_str = re.sub(r'(?<=[0-9])\s+', '', json_str)
        json_str = re.sub(r'(?<=\[)\s+(?=[0-9])', '', json_str)
        json_str = re.sub(r'(?<=\[)\s+(?=\[)', '', json_str)
        json_str = re.sub(r'(?<=\],)\s+(?=\[)', '', json_str)
        json_str = re.sub(r'(?<=\],)\s+(?=\])', '', json_str)
        json_str = re.sub(r'(?<=\])\s+(?=\])', '', json_str)
        with open(filename, "w") as file:
            file.write(json_str)
        
    def track_score(self, board, player):
        # Convert board to easily parsed format
        data = {}
        if isinstance(player, RuleBasedPlayer):
            data["active_player"] = board.active_player
            score = player.eval(board, board.active_player)
        if isinstance(player, NormRuleBasedPlayer):
            score = player.eval(board)
        elif isinstance(player, MinMaxPlayer):
            data["active_player"] = board.active_player
            score = player.minmax(board, 3)
        else:
            return
        data["board_state"] = copy.deepcopy(board.board_state)
        data["exit_states"] = copy.deepcopy(board.exit_states)
        data["start_counts"] = copy.deepcopy(board.start_counts)
        data["exit_counts"] = copy.deepcopy(board.exit_counts)
        data["score"] = score
        data["player_type"] = player.name
        self.state.append(data)