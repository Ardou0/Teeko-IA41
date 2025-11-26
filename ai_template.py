import random
from history_analyzer import HistoryAnalyzer

class TeekoAI:
    def __init__(self, game_engine, who, difficulty="2"):
        self.game_engine = game_engine
        self.who_am_i = who
        
        # Gestion simplifiée et directe
        if isinstance(difficulty, str):
            diff = difficulty.strip()
            try:
                level = int(diff)
                self.base_difficulty = max(1, min(5, level))
                # Expert (niveau 5) = adaptatif activé
                self.adaptatif = (level == 5)
            except ValueError:
                self.base_difficulty = 2
                self.adaptatif = False
        else:
            try:
                self.base_difficulty = max(1, min(5, int(difficulty)))
                self.adaptatif = (int(difficulty) == 5)
            except Exception:
                self.base_difficulty = 2
                self.adaptatif = False

        print(f"DEBUG - base_difficulty: {self.base_difficulty}, adaptatif: {self.adaptatif}")

        self.last_opponent_move = None
        self.last_move = None
        self.last_moves = []  # Pour éviter les répétitions
        self.max_repetitions = 2  # Limite de répétitions autorisées

        # Initialisation de l'analyseur d'historique
        self.analyzer = HistoryAnalyzer()
        self.move_history = []

    def record_opponent_move(self, move):
        """Enregistre le coup de l'adversaire et met à jour l'historique."""
        if move is None:
            return
        self.last_opponent_move = move
        opponent_color = 'red' if self.who_am_i == 'black' else 'black'
        self.move_history.append({'move': move, 'player': opponent_color})

    def evaluate_board(self, board):
        """Évalue l'état du plateau en tenant compte du style de l'adversaire."""
        opponent = 'red' if self.who_am_i == 'black' else 'black'
        win_patterns = self.game_engine.win_patterns
        score = 0

        # --- Section d'analyse dynamique ---
        aggression_factor = 1.0
        fork_bonus_factor = 1.0

        if len(self.move_history) > 4: # On attend d'avoir assez de données
            all_styles = self.analyzer.analyze_player_styles(self.move_history, win_patterns)
            if all_styles:
                opponent_style = all_styles.get(opponent)
                if opponent_style:
                    # Si l'adversaire est agressif, on devient plus prudent
                    if opponent_style['offensive_ratio'] > 0.6:
                        aggression_factor = 1.5
                    # Si l'adversaire est défensif, on favorise les pièges
                    if opponent_style['defensive_ratio'] > 0.6:
                        fork_bonus_factor = 1.5

        # --- Évaluation de base (valable pour tous les niveaux) ---

        # Vérifier les victoires/défaites (score terminal)
        for pattern in win_patterns:
            if all(board[pos] == self.who_am_i for pos in pattern):
                return 1000
            if all(board[pos] == opponent for pos in pattern):
                return -1000
        
        # Pénalité pour répétitions (mode expert)
        if self.adaptatif and tuple(board) in self.last_moves:
            score -= 500

        # --- Évaluation unifiée des motifs ---
        for pattern in win_patterns:
            my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
            opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)

            if my_pieces > 0 and opp_pieces > 0:
                continue # Ignorer les lignes sans avenir

            # Nos opportunités
            if my_pieces == 3:
                score += 500
            elif my_pieces == 2:
                # Bonus si c'est une fourche potentielle (2 cases vides)
                if len([p for p in pattern if board[p] is None]) == 2:
                    score += 50 * fork_bonus_factor
                else:
                    score += 25
            elif my_pieces == 1:
                score += 5

            # Menaces adverses
            if opp_pieces == 3:
                score -= 500 * aggression_factor
            elif opp_pieces == 2:
                # Pénalité accrue si c'est une menace de fourche
                if len([p for p in pattern if board[p] is None]) == 2:
                    score -= 150 * aggression_factor
                else:
                    score -= 75 * aggression_factor
            elif opp_pieces == 1:
                score -= 5

        # Bonus spécifiques au mode expert pour la réactivité
        if self.adaptatif:
            if self.last_opponent_move is not None:
                last_move_type, *last_move_positions = self.last_opponent_move
                last_pos = last_move_positions[0] if last_move_type == 'drop' else last_move_positions[1]

                for pattern in win_patterns:
                    if last_pos in pattern:
                        if sum(1 for p in pattern if board[p] == opponent) == 3:
                            score -= 1000  # Urgence de blocage
                        elif sum(1 for p in pattern if board[p] == opponent) == 2:
                            score -= 250 # Priorité élevée

        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing_player):
        """Algorithme MinMax avec élagage alpha-bêta."""
        if depth == 0:
            return self.evaluate_board(board)
        if is_maximizing_player:
            best_value = float('-inf')
            for move in self.get_all_possible_moves(board, self.who_am_i):
                new_board = self.simulate_move(board, move, self.who_am_i)
                value = self.minimax(new_board, depth - 1, alpha, beta, False)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  # Élagage beta
            return best_value
        else:
            best_value = float('inf')
            opponent = 'red' if self.who_am_i == 'black' else 'black'
            for move in self.get_all_possible_moves(board, opponent):
                new_board = self.simulate_move(board, move, opponent)
                value = self.minimax(new_board, depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  # Élagage alpha
            return best_value

    def get_all_possible_moves(self, board, player):
        """Récupère tous les coups possibles pour un joueur donné."""
        moves = []
        if board is None:
            return moves  # Retourne une liste vide si le plateau est invalide

        # Compter le nombre total de pions posés sur le plateau
        total_pieces_placed = 0
        for pos in range(25):
            if board[pos] is not None:
                total_pieces_placed += 1

        if total_pieces_placed < 8:  # Phase de pose
            for position in range(25):
                if board[position] is None:
                    moves.append(('drop', position))
        else:  # Phase de déplacement
            for from_position in range(25):
                if board[from_position] == player:
                    for to_position in range(25):
                        if board[to_position] is None and self.is_adjacent(from_position, to_position):
                            moves.append(('move', from_position, to_position))
        return moves

    def is_adjacent(self, from_position, to_position):
        """Vérifie si `to_position` est adjacent à `from_position`."""
        from_row, from_col = divmod(from_position, 5)
        to_row, to_col = divmod(to_position, 5)
        return abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1 and from_position != to_position

    def simulate_move(self, board, move, player):
        """Simule un coup sur une copie du plateau."""
        new_board = board.copy()
        if move[0] == 'drop':
            new_board[move[1]] = player
        elif move[0] == 'move':
            new_board[move[1]] = None
            new_board[move[2]] = player
        return new_board

    def adaptive_depth(self, board):
        """Calcule la profondeur de recherche en fonction de la difficulté."""
        # Détecter la phase (drop ou move)
        total_pieces = sum(1 for pos in range(25) if board[pos] is not None)
        is_drop_phase = total_pieces < 8
        
        if not self.adaptatif:
            # Mode débutant, normal, pro : profondeur réduite en phase de drop
            base_depth = self.base_difficulty
            
            if is_drop_phase:
                # Réduction significative en phase de drop
                if base_depth >= 4:  # Pro
                    depth = 2
                elif base_depth == 2:  # Normal
                    depth = 1
                else:  # Débutant
                    depth = 1
            else:
                # Phase move : profondeur normale
                depth = base_depth
            return depth
        else:
            # Mode expert : profondeur adaptative 
            possible_moves = len(self.get_all_possible_moves(board, self.who_am_i))
            depth = min(5, 5 + (8 - possible_moves // 2))
            
            # Réduire la profondeur en phase de drop
            if is_drop_phase:
                if total_pieces < 4:  # Tout début
                    depth = 2
                else:  # Fin de phase drop
                    depth = 3
                     
            print(f"Profondeur de recherche pour {self.who_am_i} (expert): {depth}")
            return depth


    def choose_best_move(self):
        """Choisit le meilleur coup avec une priorité aux blocages et opportunités en mode 'expert'."""
        board = self.game_engine.get_board()
        all_moves = self.get_all_possible_moves(board, self.who_am_i)

        # Recherche d'un coup gagnant immédiat avant toute autre considération
        for move in all_moves:
            temp_board = self.simulate_move(board, move, self.who_am_i)
            for pattern in self.game_engine.win_patterns:
                if all(temp_board[pos] == self.who_am_i for pos in pattern):
                    print(f"IA ({self.who_am_i}) a trouvé un coup gagnant immédiat : {move}")
                    return move

        # Recherche d'un blocage de victoire adverse immédiate
        opponent = 'red' if self.who_am_i == 'black' else 'black'
        opponent_moves = self.get_all_possible_moves(board, opponent)
        blocking_moves = []
        
        opponent_win_positions = []
        for opp_move in opponent_moves:
            is_winning = False
            temp_board = self.simulate_move(board, opp_move, opponent)
            for pattern in self.game_engine.win_patterns:
                if all(temp_board[pos] == opponent for pos in pattern):
                    is_winning = True
                    break
            if is_winning:
                # Déterminer la position cible du coup gagnant de l'adversaire
                win_pos = opp_move[1] if opp_move[0] == 'drop' else opp_move[2]
                if win_pos not in opponent_win_positions:
                    opponent_win_positions.append(win_pos)
        
        # Si des positions de victoire adverse existent, trouver nos coups pour les bloquer
        if opponent_win_positions:
            for block_pos in opponent_win_positions:
                for my_move in all_moves:
                    # Déterminer la position cible de notre propre coup
                    my_move_pos = my_move[1] if my_move[0] == 'drop' else my_move[2]
                    if my_move_pos == block_pos:
                        if my_move not in blocking_moves:
                            blocking_moves.append(my_move)
            
            # S'il y a des coups de blocage possibles, en choisir un
            if blocking_moves:
                chosen_block = random.choice(blocking_moves)
                print(f"IA ({self.who_am_i}) a trouvé un blocage nécessaire : {chosen_block}")
                return chosen_block

        depth = self.adaptive_depth(board)
        best_value = float('-inf')
        best_moves = []
        opponent = 'red' if self.who_am_i == 'black' else 'black'

        # En mode débutant, normal, pro, ajouter une perturbation aléatoire
        if not self.adaptatif:
            if all_moves:
                # Choisir aléatoirement parmi les 3 meilleurs coups (au lieu du meilleur seul)
                move_scores = []
                for move in all_moves:
                    new_board = self.simulate_move(board, move, self.who_am_i)
                    move_value = self.minimax(new_board, depth - 1, float('-inf'), float('inf'), False)
                    move_scores.append((move, move_value))

                # Trier les coups par score (du meilleur au pire)
                move_scores.sort(key=lambda x: x[1], reverse=True)

                # Prendre les 3 meilleurs coups (ou moins s'il n'y en a pas assez)
                top_moves = [move for move, score in move_scores[:min(3, len(move_scores))]]
                if top_moves:
                    return random.choice(top_moves)

        # Trouver les coups urgents (blocages ou victoires immédiates)
        urgent_moves = []
        if self.last_opponent_move is not None:
            last_move_type, *last_move_positions = self.last_opponent_move
            if last_move_type == 'drop':
                last_pos = last_move_positions[0]
            elif last_move_type == 'move':
                last_pos = last_move_positions[1]

            for pattern in self.game_engine.win_patterns:
                if last_pos in pattern:
                    opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)
                    if opp_pieces == 3:  # Motif presque gagnant pour l'adversaire
                        for pos in pattern:
                            if board[pos] is None:
                                move = ('drop', pos) if len([p for p in board if p is not None]) < 8 else None
                                if move is None:
                                    for from_pos in range(25):
                                        if board[from_pos] == self.who_am_i and self.is_adjacent(from_pos, pos):
                                            move = ('move', from_pos, pos)
                                            break
                                if move is not None and move not in urgent_moves:
                                    urgent_moves.append(move)

        # En mode "expert", ignorer les blocages dans 30% des cas pour forcer des erreurs chez l'adversaire
        if self.adaptatif and urgent_moves and random.random() < 0.3:
            urgent_moves = []  # Ignorer les blocages aléatoirement pour créer des opportunités

        # En mode "expert", évaluer d'abord les coups urgents
        if self.adaptatif and urgent_moves:
            for move in urgent_moves:
                new_board = self.simulate_move(board, move, self.who_am_i)
                move_value = self.minimax(new_board, depth - 1, float('-inf'), float('inf'), False)
                if move_value > best_value:
                    best_value = move_value
                    best_moves = [move]
                elif move_value == best_value:
                    best_moves.append(move)
        else:
            # Sinon, évaluer tous les coups possibles
            for move in self.get_all_possible_moves(board, self.who_am_i):
                new_board = self.simulate_move(board, move, self.who_am_i)
                move_value = self.minimax(new_board, depth - 1, float('-inf'), float('inf'), False)
                if move_value > best_value:
                    best_value = move_value
                    best_moves = [move]
                elif move_value == best_value:
                    best_moves.append(move)

        # En mode "expert", éviter les répétitions
        if self.adaptatif and best_moves:
            filtered_moves = []
            for move in best_moves:
                new_board = self.simulate_move(board, move, self.who_am_i)
                if tuple(new_board) not in self.last_moves:
                    filtered_moves.append(move)
            best_moves = filtered_moves if filtered_moves else best_moves

        return random.choice(best_moves) if best_moves else None

    def get_difficulty_name(self):
        """Retourne le nom du niveau de difficulté."""
        level_names = {
            1: "Débutant",
            2: "Normal", 
            4: "Pro",
            5: "Expert"
        }
        
        if self.adaptatif:
            return "Expert"
        else:
            return level_names.get(self.base_difficulty, f"niveau {self.base_difficulty}")

    def make_move(self):
        """Effectue le meilleur coup et met à jour l'historique."""
        best_move = self.choose_best_move()
        
        if best_move is not None:
            self.move_history.append({'move': best_move, 'player': self.who_am_i})
            self.last_move = best_move
            
            # Exécuter le coup sur le moteur de jeu (garder les positions 0-24 pour l'exécution)
            if best_move[0] == 'drop':
                self.game_engine.drop_piece(best_move[1])
            elif best_move[0] == 'move':
                self.game_engine.move_piece(best_move[1], best_move[2])

            # Créer une copie du best_move avec positions converties 0-24 → 1-25 pour l'affichage
            if best_move[0] == 'drop':
                display_move = ('drop', best_move[1] + 1)  # ← +1 ici
            else:  # 'move'
                display_move = ('move', best_move[1] + 1, best_move[2] + 1)  # ← +1 ici
            
            # Affichage avec positions 1-25
            niveau = self.get_difficulty_name()
            print(f"IA ({self.who_am_i} - {niveau}) a joué: {display_move}")

            # Enregistrer le plateau actuel pour éviter les répétitions
            if self.adaptatif:
                current_board = tuple(self.game_engine.get_board())
                self.last_moves.append(current_board)
                if len(self.last_moves) > 3:
                    self.last_moves.pop(0)
            
        return best_move