# history_analyzer.py

class HistoryAnalyzer:
    def __init__(self):
        """
        Initialise l'analyseur d'historique.
        Définit les zones stratégiques du plateau de 5x5.
        """
        self.corners = {0, 4, 20, 24}
        self.center = {12}
        self.edges = {1, 2, 3, 5, 9, 10, 14, 15, 19, 21, 22, 23}

    def _simulate_move(self, board, move, player):
        """Simule un coup sur une copie du plateau."""
        new_board = list(board)
        move_type, *positions = move
        if move_type == 'drop':
            new_board[positions[0]] = player
        elif move_type == 'move':
            new_board[positions[0]] = None
            new_board[positions[1]] = player
        return new_board

    def _reconstruct_board_at_turn(self, move_history, turn_index):
        """Reconstruit l'état du plateau à un tour donné en rejouant l'historique."""
        board = [None] * 25
        for i in range(turn_index):
            entry = move_history[i]
            board = self._simulate_move(board, entry['move'], entry['player'])
        return board

    def analyze_player_styles(self, move_history, win_patterns):
        """
        Analyse l'historique complet pour déterminer le style de jeu (offensif/défensif)
        de CHAQUE joueur.
        """
        styles = {
            'black': {'offensive': 0, 'defensive': 0, 'neutral': 0},
            'red': {'offensive': 0, 'defensive': 0, 'neutral': 0}
        }

        if len(move_history) < 2:
            return None  # Pas assez de données

        for i, entry in enumerate(move_history):
            player = entry['player']
            move = entry['move']
            opponent = 'red' if player == 'black' else 'black'
            
            board_before = self._reconstruct_board_at_turn(move_history, i)
            
            target_pos = move[1] if move[0] == 'drop' else move[2]
            
            move_category = 'neutral'
            is_defensive = False
            for pattern in win_patterns:
                if target_pos in pattern:
                    my_pieces_before = sum(1 for pos in pattern if board_before[pos] == player)
                    opp_pieces_before = sum(1 for pos in pattern if board_before[pos] == opponent)

                    if opp_pieces_before >= 2 and my_pieces_before == 0:
                        is_defensive = True
                        break  # C'est un blocage, la plus haute priorité

                    if my_pieces_before >= 1:
                        move_category = 'offensive'
            
            if is_defensive:
                styles[player]['defensive'] += 1
            else:
                styles[player][move_category] += 1
        
        final_analysis = {}
        for player in ['black', 'red']:
            total_moves = sum(styles[player].values())
            if total_moves > 0:
                final_analysis[player] = {
                    'offensive_ratio': round(styles[player]['offensive'] / total_moves, 2),
                    'defensive_ratio': round(styles[player]['defensive'] / total_moves, 2),
                    'neutral_ratio': round(styles[player]['neutral'] / total_moves, 2)
                }
            else:
                final_analysis[player] = {'offensive_ratio': 0, 'defensive_ratio': 0, 'neutral_ratio': 1}

        return final_analysis
    
    def analyze_strategic_positions(self, move_history, player_color):
        """
        Analyse l'historique des coups de placement (drop) d'un joueur 
        pour déterminer ses préférences de zone (centre, coins, bords).
        """
        drop_moves = [item['move'][1] for item in move_history if item['player'] == player_color and item['move'][0] == 'drop']
        total_drops = len(drop_moves)
        if total_drops == 0:
            return {'center': 0, 'corners': 0, 'edges': 0}

        analysis = {
            'center': sum(1 for pos in drop_moves if pos in self.center) / total_drops,
            'corners': sum(1 for pos in drop_moves if pos in self.corners) / total_drops,
            'edges': sum(1 for pos in drop_moves if pos in self.edges) / total_drops
        }
        return {k: round(v, 2) for k, v in analysis.items()}
