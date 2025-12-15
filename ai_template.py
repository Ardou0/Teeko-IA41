import random
from history_analyzer import HistoryAnalyzer

class TeekoAI:
    """
    Classe implémentant l'intelligence artificielle pour le jeu Teeko.
    
    Cette classe contient la logique de décision de l'IA, y compris l'algorithme
    Minimax avec élagage alpha-bêta, une fonction d'évaluation heuristique 
    complexe, et plusieurs optimisations pour améliorer les performances et la 
    pertinence stratégique des coups.
    """
    def __init__(self, game_engine, who, difficulty="2"):
        """
        Initialise l'intelligence artificielle.

        :param game_engine: L'instance du moteur de jeu pour interagir avec l'état de la partie.
        :param who: La couleur du joueur que l'IA incarne ('black' ou 'red').
        :type who: str
        :param difficulty: Le niveau de difficulté de l'IA, de "1" à "5".
                         Le niveau "5" active le mode expert adaptatif.
        :type difficulty: str
        """
        self.game_engine = game_engine
        self.who_am_i = who
        
        # Configuration de la difficulté et du mode adaptatif
        if isinstance(difficulty, str):
            diff = difficulty.strip()
            try:
                level = int(diff)
                self.base_difficulty = max(1, min(5, level))
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
        self.last_moves = []
        self.max_repetitions = 2

        # Modules d'analyse et de performance
        self.analyzer = HistoryAnalyzer()
        self.move_history = []
        self.transposition_table = {}

        # Matrice de valeurs pour l'évaluation positionnelle des cases.
        # Le centre et les zones adjacentes ont plus de valeur.
        self.positional_values = [
            1, 2, 2, 2, 1, 
            2, 3, 4, 3, 2, 
            2, 4, 5, 4, 2,
            2, 3, 4, 3, 2, 
            1, 2, 2, 2, 1
        ]

    def record_opponent_move(self, move):
        """
        Enregistre le dernier coup de l'adversaire pour l'analyse historique.

        :param move: Le coup joué par l'adversaire.
        """
        if move is None: return
        self.last_opponent_move = move
        opponent_color = 'red' if self.who_am_i == 'black' else 'black'
        self.move_history.append({'move': move, 'player': opponent_color})

    def evaluate_board(self, board):
        """
        Évalue l'état d'un plateau et lui attribue un score numérique.

        Cette fonction heuristique est au cœur de la décision de l'IA. Le score
        est calculé en fonction de plusieurs critères stratégiques :
        - États terminaux (victoire/défaite).
        - Contrôle positionnel (valeur des cases occupées).
        - Mobilité des pions (nombre de mouvements possibles).
        - Menaces directes et potentiel offensif (alignements de 2 ou 3 pions).
        - Style de jeu de l'adversaire (facteur d'agressivité).

        :param board: L'état du plateau à évaluer.
        :type board: list
        :return: Le score numérique représentant l'avantage de la position.
                 Un score positif favorise l'IA, un score négatif l'adversaire.
        :rtype: int
        """
        opponent = 'red' if self.who_am_i == 'black' else 'black'
        win_patterns = self.game_engine.win_patterns
        score = 0
        is_move_phase = sum(1 for pos in board if pos is not None) >= 8

        # Analyse du style adverse pour ajuster la stratégie
        aggression_factor = 1.0
        if len(self.move_history) > 4:
            all_styles = self.analyzer.analyze_player_styles(self.move_history, win_patterns)
            if all_styles and (opponent_style := all_styles.get(opponent)) and opponent_style['offensive_ratio'] > 0.6:
                aggression_factor = 1.5

        # Évaluation des états terminaux (priorité absolue)
        for pattern in win_patterns:
            if all(board[pos] == self.who_am_i for pos in pattern): return 10000
            if all(board[pos] == opponent for pos in pattern): return -10000
        
        # Pénalité pour les répétitions d'états en mode expert
        if self.adaptatif and tuple(board) in self.last_moves:
            score -= 1000

        # Évaluation du contrôle positionnel
        positional_score = sum(self.positional_values[i] if board[i] == self.who_am_i else -self.positional_values[i] for i in range(25) if board[i])
        score += positional_score * 2

        # Évaluation de la mobilité en phase de mouvement
        if is_move_phase:
            my_moves_count = len(self.get_all_possible_moves(board, self.who_am_i))
            opp_moves_count = len(self.get_all_possible_moves(board, opponent))
            score += (my_moves_count - opp_moves_count) * 3

        # Évaluation des menaces et du potentiel offensif
        my_threats_3, opp_threats_3 = 0, 0
        for pattern in win_patterns:
            my_pieces = sum(1 for pos in pattern if board[pos] == self.who_am_i)
            opp_pieces = sum(1 for pos in pattern if board[pos] == opponent)

            if my_pieces > 0 and opp_pieces > 0: continue # Ligne sans potentiel

            if my_pieces == 3: my_threats_3 += 1
            elif my_pieces == 2: score += 20
            elif my_pieces == 1: score += 5

            if opp_pieces == 3: opp_threats_3 += 1
            elif opp_pieces == 2: score -= 30 * aggression_factor
            elif opp_pieces == 1: score -= 5 * aggression_factor

        score += my_threats_3 * 200
        score -= opp_threats_3 * 250 * aggression_factor
        return score

    def _check_board_winner(self, board):
        """
        Vérifie s'il y a un gagnant sur le plateau donné.

        :param board: L'état du plateau à vérifier.
        :type board: list
        :return: La couleur du joueur gagnant, ou None si personne n'a gagné.
        :rtype: str or None
        """
        for pattern in self.game_engine.win_patterns:
            if all(board[pos] and board[pos] == board[pattern[0]] for pos in pattern):
                return board[pattern[0]]
        return None

    def minimax(self, board, depth, alpha, beta, is_maximizing_player):
        """
        Implémente l'algorithme Minimax avec élagage alpha-bêta.

        Cette fonction explore récursivement l'arbre des coups possibles pour
        trouver le meilleur coup. Elle est optimisée par :
        1. Table de Transposition : met en cache les états déjà évalués pour
           éviter les calculs redondants.
        2. Ordre des Coups : évalue les coups les plus prometteurs en premier
           pour maximiser l'efficacité de l'élagage.

        :param board: L'état du plateau à partir duquel chercher.
        :type board: list
        :param depth: La profondeur de recherche restante.
        :type depth: int
        :param alpha: La meilleure valeur trouvée jusqu'à présent pour le joueur maximisant.
        :type alpha: float
        :param beta: La meilleure valeur trouvée jusqu'à présent pour le joueur minimisant.
        :type beta: float
        :param is_maximizing_player: True si c'est le tour de l'IA, False pour l'adversaire.
        :type is_maximizing_player: bool
        :return: Le meilleur score d'évaluation trouvé pour la branche explorée.
        :rtype: float
        """
        original_alpha = alpha
        board_key = tuple(board)

        # 1. Consultation de la table de transposition
        if board_key in self.transposition_table:
            entry = self.transposition_table[board_key]
            if entry['depth'] >= depth:
                if entry['flag'] == 'EXACT': return entry['score']
                elif entry['flag'] == 'LOWER': alpha = max(alpha, entry['score'])
                elif entry['flag'] == 'UPPER': beta = min(beta, entry['score'])
                if alpha >= beta: return entry['score']

        winner = self._check_board_winner(board)
        if depth == 0 or winner:
            return self.evaluate_board(board)

        player = self.who_am_i if is_maximizing_player else ('red' if self.who_am_i == 'black' else 'black')
        
        # 2. Tri des coups pour optimiser l'élagage
        moves = self.get_all_possible_moves(board, player)
        move_scores = [(move, self.evaluate_board(self.simulate_move(board, move, player))) for move in moves]
        move_scores.sort(key=lambda x: x[1], reverse=is_maximizing_player)
        sorted_moves = [move for move, score in move_scores]

        best_value = float('-inf') if is_maximizing_player else float('inf')
        for move in sorted_moves:
            new_board = self.simulate_move(board, move, player)
            value = self.minimax(new_board, depth - 1, alpha, beta, not is_maximizing_player)
            if is_maximizing_player:
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, best_value)
            if beta <= alpha:
                break # Élagage
    
        # 3. Sauvegarde du résultat dans la table de transposition
        flag = 'EXACT'
        if best_value <= original_alpha: flag = 'UPPER'
        elif best_value >= beta: flag = 'LOWER'
        self.transposition_table[board_key] = {'score': best_value, 'depth': depth, 'flag': flag}
        
        return best_value

    def get_all_possible_moves(self, board, player):
        """
        Génère une liste de tous les coups légaux pour un joueur donné.

        :param board: L'état actuel du plateau.
        :type board: list
        :param player: Le joueur pour lequel générer les coups.
        :type player: str
        :return: Une liste de tuples représentant les coups possibles.
                 Format: ('drop', position) ou ('move', from, to).
        :rtype: list
        """
        moves = []
        if board is None: return moves
        if sum(1 for pos in board if pos is not None) < 8:
            return [('drop', pos) for pos in range(25) if board[pos] is None]
        else:
            player_pieces = [i for i, piece in enumerate(board) if piece == player]
            for from_pos in player_pieces:
                r, c = divmod(from_pos, 5)
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and board[nr * 5 + nc] is None:
                            moves.append(('move', from_pos, nr * 5 + nc))
            return moves

    def simulate_move(self, board, move, player):
        """
        Applique un coup sur une copie du plateau pour simuler son résultat.

        :param board: Le plateau d'origine.
        :type board: list
        :param move: Le coup à simuler.
        :type move: tuple
        :param player: Le joueur qui effectue le coup.
        :type player: str
        :return: Un nouveau plateau avec le coup appliqué.
        :rtype: list
        """
        new_board = board.copy()
        if move[0] == 'drop': new_board[move[1]] = player
        else: new_board[move[1]], new_board[move[2]] = None, player
        return new_board
    
    def calculate_threats(self, board, player):
        """
        Compte le nombre de menaces (alignements de 3 pions) pour un joueur.

        :param board: L'état du plateau.
        :type board: list
        :param player: Le joueur dont on veut compter les menaces.
        :type player: str
        :return: Le nombre de menaces de 3 pions non bloquées.
        :rtype: int
        """
        threats, opponent = 0, 'red' if player == 'black' else 'black'
        for pattern in self.game_engine.win_patterns:
            if sum(1 for p in pattern if board[p] == player) == 3 and sum(1 for p in pattern if board[p] == opponent) == 0:
                threats += 1
        return threats

    def adaptive_depth(self, board):
        """
        Calcule dynamiquement la profondeur de recherche de l'IA.

        La profondeur est ajustée en fonction du niveau de difficulté et de la 
        phase de jeu pour équilibrer performance et pertinence.

        :param board: L'état actuel du plateau.
        :type board: list
        :return: La profondeur de recherche à utiliser.
        :rtype: int
        """
        total_pieces = sum(1 for pos in board if pos is not None)
        is_drop_phase = total_pieces < 8
        if not self.adaptatif:
            depth = self.base_difficulty
            if is_drop_phase: depth = 2 if depth >= 4 else 1
            return depth
        else:
            possible_moves = len(self.get_all_possible_moves(board, self.who_am_i))
            depth = min(5, 5 + (8 - possible_moves // 2))
            if is_drop_phase: depth = 3 if total_pieces > 4 else 2
            print(f"Profondeur de recherche pour {self.who_am_i} (expert): {depth}")
            return depth

    def choose_best_move(self):
        """
        Orchestre la recherche du meilleur coup à jouer.

        Cette fonction de haut niveau suit une stratégie en plusieurs étapes :
        1. Vider la table de transposition pour la nouvelle recherche.
        2. Vérifier s'il existe un coup gagnant immédiat.
        3. Vérifier s'il faut bloquer une victoire imminente de l'adversaire.
        4. Gérer la logique de bluff en mode expert.
        5. Lancer la recherche Minimax pour évaluer tous les autres coups.
        6. Appliquer un bonus pour les coups créant une "fourchette".
        7. Sélectionner le meilleur coup parmi les candidats.

        :return: Le meilleur coup trouvé par l'IA.
        :rtype: tuple or None
        """
        self.transposition_table = {}

        board = self.game_engine.get_board()
        all_moves = self.get_all_possible_moves(board, self.who_am_i)
        opponent = 'red' if self.who_am_i == 'black' else 'black'

        # Recherche de coup gagnant immédiat
        for move in all_moves:
            temp_board = self.simulate_move(board, move, self.who_am_i)
            if self._check_board_winner(temp_board) == self.who_am_i:
                print(f"IA ({self.who_am_i}) a trouvé un coup gagnant immédiat : {move}")
                return move

        # Recherche de blocage de victoire adverse
        blocking_moves = []
        for opp_move in self.get_all_possible_moves(board, opponent):
            temp_board = self.simulate_move(board, opp_move, opponent)
            if self._check_board_winner(temp_board) == opponent:
                block_pos = opp_move[1] if opp_move[0] == 'drop' else opp_move[2]
                for my_move in all_moves:
                    if (my_move[1] if my_move[0] == 'drop' else my_move[2]) == block_pos:
                        blocking_moves.append(my_move)
        
        # Logique de blocage et de bluff
        if blocking_moves:
            if self.adaptatif:
                current_score = self.evaluate_board(board)
                if current_score > 100 and random.random() < 0.35:
                    print(f"IA ({self.who_am_i}) BLUFFE! Ignore un blocage. Score: {current_score}")
                else: return random.choice(blocking_moves)
            else: return random.choice(blocking_moves)

        depth = self.adaptive_depth(board)
        best_value, best_moves = float('-inf'), []

        # Pour les niveaux non-experts, introduire de la variabilité
        if not self.adaptatif and all_moves:
            move_scores = sorted([(m, self.minimax(self.simulate_move(board, m, self.who_am_i), depth - 1, float('-inf'), float('inf'), False)) for m in all_moves], key=lambda x: x[1], reverse=True)
            top_moves = [move for move, score in move_scores[:min(3, len(move_scores))]]
            return random.choice(top_moves) if top_moves else None

        # Recherche Minimax pour le mode expert
        threats_before = self.calculate_threats(board, self.who_am_i)
        for move in all_moves:
            new_board = self.simulate_move(board, move, self.who_am_i)
            move_value = self.minimax(new_board, depth - 1, float('-inf'), float('inf'), False)
            
            # Bonus pour la création de fourchettes
            if (self.calculate_threats(new_board, self.who_am_i) - threats_before) >= 2:
                move_value += 350
                print(f"IA ({self.who_am_i}) a détecté une fourchette potentielle avec le coup {move}")

            if move_value > best_value:
                best_value, best_moves = move_value, [move]
            elif move_value == best_value:
                best_moves.append(move)

        # Anti-répétition en mode expert
        if self.adaptatif and best_moves:
            filtered_moves = [m for m in best_moves if tuple(self.simulate_move(board, m, self.who_am_i)) not in self.last_moves]
            if filtered_moves: best_moves = filtered_moves

        return random.choice(best_moves) if best_moves else None

    def get_difficulty_name(self):
        """
        Retourne le nom du niveau de difficulté actuel.
        
        :return: Le nom de la difficulté.
        :rtype: str
        """
        level_names = {1: "Débutant", 2: "Normal", 4: "Pro"}
        return "Expert" if self.adaptatif else level_names.get(self.base_difficulty, f"Niveau {self.base_difficulty}")

    def make_move(self):
        """
        Fonction principale appelée pour que l'IA joue son tour.

        Elle lance la recherche du meilleur coup, l'exécute sur le moteur
        de jeu et met à jour son historique interne.

        :return: Le coup qui a été joué.
        :rtype: tuple or None
        """
        best_move = self.choose_best_move()
        if best_move:
            self.move_history.append({'move': best_move, 'player': self.who_am_i})
            self.last_move = best_move
            
            if best_move[0] == 'drop': self.game_engine.drop_piece(best_move[1])
            else: self.game_engine.move_piece(best_move[1], best_move[2])

            display_move = ('drop', best_move[1] + 1) if best_move[0] == 'drop' else ('move', best_move[1] + 1, best_move[2] + 1)
            print(f"IA ({self.who_am_i} - {self.get_difficulty_name()}) a joué: {display_move}")

            if self.adaptatif:
                current_board = tuple(self.game_engine.get_board())
                self.last_moves.append(current_board)
                if len(self.last_moves) > 3: self.last_moves.pop(0)
        return best_move
