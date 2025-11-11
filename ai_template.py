import random

class TeekoAI:
    def __init__(self, game_engine, who, difficulty=3):

        self.game_engine = game_engine
        self.who_am_i = who
        # Normalisation de la difficulté
        # - "teacher" => mode adaptatif
        # - "standard" ou entier => mode non adaptatif avec base_difficulty numérique
        self.adaptatif = False
        if isinstance(difficulty, str):
            d = difficulty.strip().lower()
            if d == "teacher":
                self.adaptatif = True
                # Valeur arbitraire non utilisée en mode adaptatif, mais on la définit proprement
                self.base_difficulty = 4
            elif d == "standard":
                self.base_difficulty = 2
            else:
                # Si la chaîne représente un nombre, on convertit
                try:
                    self.base_difficulty = max(1, int(d))
                except ValueError:
                    # Valeur par défaut sûre
                    self.base_difficulty = 2
        else:
            # Entier fourni
            try:
                self.base_difficulty = max(1, int(difficulty))
            except Exception:
                self.base_difficulty = 2

        self.last_opponent_move = None
        self.last_move = None
        self.last_moves = []  # Pour éviter les répétitions
        self.max_repetitions = 2  # Limite de répétitions autorisées

    def evaluate_board(self, board):
        """Évalue l'état du plateau avec une stratégie plus agressive en mode 'teacher'."""
        opponent = 'white' if self.who_am_i == 'black' else 'black'
        win_patterns = self.game_engine.win_patterns
        score = 0

        # Vérifier les répétitions (uniquement en mode "teacher")
        if self.adaptatif:
            current_move = tuple(board)
            if self.last_moves.count(current_move) >= self.max_repetitions:
                score -= 500  # Pénalité pour les répétitions

        # Vérifier les victoires/défaites
        for pattern in win_patterns:
            if all(board[pos] == self.who_am_i for pos in pattern):
                return 1000
            if all(board[pos] == opponent for pos in pattern):
                return -1000

        # En mode standard, l'IA est moins réactive
        if not self.adaptatif:
            for pattern in win_patterns:
                my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
                opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)

                if my_pieces == 3:
                    score += 500
                elif my_pieces == 2:
                    score += 50  # Moins que l'IA "teacher"
                # L'IA standard ignore les motifs à 1 pion

                if opp_pieces == 3:
                    score -= 500  # Moins pénalisant
                # L'IA standard ignore les motifs à 2 pions de l'adversaire
        else:
            # Logique complète pour l'IA "teacher"
            # Analyser le dernier coup de l'adversaire
            if self.last_opponent_move is not None:
                last_move_type, *last_move_positions = self.last_opponent_move
                if last_move_type == 'drop':
                    last_pos = last_move_positions[0]
                elif last_move_type == 'move':
                    last_pos = last_move_positions[1]

                for pattern in win_patterns:
                    if last_pos in pattern:
                        opp_pieces_in_pattern = sum(1 for pos in pattern if board[pos] == opponent)
                        my_pieces_in_pattern = sum(1 for pos in pattern if board[pos] == self.who_am_i)

                        if opp_pieces_in_pattern == 3 and my_pieces_in_pattern == 0:
                            score -= 2000  # Urgence absolue pour bloquer
                        elif opp_pieces_in_pattern == 2 and my_pieces_in_pattern == 0:
                            score -= 500  # Priorité très élevée

            # Évaluer les motifs partiellement complétés
            for pattern in win_patterns:
                my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
                opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)

                if my_pieces == 3 and opp_pieces == 0:
                    score += 1000
                elif my_pieces == 2 and opp_pieces == 0:
                    score += 200
                elif my_pieces == 1 and opp_pieces == 0:
                    score += 20

                if opp_pieces == 3 and my_pieces == 0:
                    score -= 1000
                elif opp_pieces == 2 and my_pieces == 0:
                    score -= 500
                elif opp_pieces == 1 and my_pieces == 0:
                    score -= 20

        # Récompenser les opportunités de victoire immédiate (plus en mode "teacher")
        for pattern in win_patterns:
            my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
            if my_pieces == 3:
                score += 2000 if self.adaptatif else 1000

        # En mode "teacher", récompenser les coups qui forcent l'adversaire à se défendre
        if self.adaptatif:
            for pattern in win_patterns:
                my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
                opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)
                empty_pos = [pos for pos in pattern if board[pos] is None]

                if my_pieces == 2 and opp_pieces == 0 and len(empty_pos) == 2:
                    score += 100  # Récompenser les "pièges"

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
            opponent = 'white' if self.who_am_i == 'black' else 'black'
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
        if not self.adaptatif:
            # Sécuriser la conversion en entier
            try:
                bd = max(1, int(self.base_difficulty))
            except Exception:
                bd = 2
            # Profondeur simple et légère pour le mode standard
            return max(1, bd - 1)
        else:
            # Mode "teacher" : profondeur plus élevée et adaptative
            possible_moves = len(self.get_all_possible_moves(board, self.who_am_i))
            depth = min(5, 5 + (8 - possible_moves // 2))  # borne supérieure 5
            print(f"Profondeur de recherche pour {self.who_am_i} (mode teacher): {depth}")
            return depth


    def choose_best_move(self):
        """Choisit le meilleur coup avec une priorité aux blocages et opportunités en mode 'teacher'."""
        board = self.game_engine.get_board()
        depth = self.adaptive_depth(board)
        best_value = float('-inf')
        best_moves = []
        opponent = 'white' if self.who_am_i == 'black' else 'black'

        # En mode standard, ajouter une perturbation aléatoire
        if not self.adaptatif:
            all_moves = self.get_all_possible_moves(board, self.who_am_i)
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

        # En mode "teacher", ignorer les blocages dans 30% des cas pour forcer des erreurs chez l'adversaire
        if self.adaptatif and urgent_moves and random.random() < 0.3:
            urgent_moves = []  # Ignorer les blocages aléatoirement pour créer des opportunités

        # En mode "teacher", évaluer d'abord les coups urgents
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

        # En mode "teacher", éviter les répétitions
        if self.adaptatif and best_moves:
            filtered_moves = []
            for move in best_moves:
                new_board = self.simulate_move(board, move, self.who_am_i)
                if tuple(new_board) not in self.last_moves:
                    filtered_moves.append(move)
            best_moves = filtered_moves if filtered_moves else best_moves

        return random.choice(best_moves) if best_moves else None

    def make_move(self):
        """Effectue le meilleur coup et met à jour l'historique."""
        best_move = self.choose_best_move()
        if best_move is not None:
            self.last_move = best_move
            if best_move[0] == 'drop':
                self.game_engine.drop_piece(best_move[1])
            elif best_move[0] == 'move':
                self.game_engine.move_piece(best_move[1], best_move[2])

            # Enregistrer le plateau actuel pour éviter les répétitions (en mode "teacher")
            if self.adaptatif:
                self.last_moves.append(tuple(self.game_engine.get_board()))
                if len(self.last_moves) > 3:  # Garder seulement les 3 derniers coups
                    self.last_moves.pop(0)

        print(f"IA ({self.who_am_i} - {'teacher' if self.adaptatif else 'standard'}) a joué: {best_move}")
