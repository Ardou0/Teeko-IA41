class TeekoGame:
    def __init__(self):
        """
        Le constructeur de la classe TeekoGame.

        Initialise le jeu Teeko avec un plateau vide et un état de jeu initial. 
        Le plateau est une liste de 25 éléments. Le joueur noir commence.
        La partie débute en phase de placement ('drop').
        
        :param self: L'instance de l'objet.
        :return: Aucun.
        """
        self.board = [None] * 25  # Plateau de 5x5 représenté par une liste
        self.current_player = 'black'  # Le joueur noir commence
        self.phase = 'drop'  # Le jeu commence par la phase de placement
        self.turn_count = 0
        self.winner = None
        self.win_patterns = self.generate_win_patterns()
        
    def reset(self):
        """
        Réinitialise le jeu à son état initial.

        Utile pour commencer une nouvelle partie sans créer un nouvel objet. 
        Le plateau est vidé, le joueur et la phase sont réinitialisés.

        :param self: L'instance de l'objet.
        :return: Aucun.
        """
        self.board = [None] * 25
        self.current_player = 'black'
        self.phase = 'drop'
        self.turn_count = 0
        self.winner = None
        
    def get_board(self):
        """
        Retourne l'état actuel du plateau.

        :param self: L'instance de l'objet.
        :return: Une liste de 25 éléments représentant le plateau. 
                 Chaque élément est soit None, 'black', ou 'red'.
        :rtype: list
        """
        return self.board

    def get_current_player(self):
        """
        Retourne le joueur actuel.

        :param self: L'instance de l'objet.
        :return: La couleur du joueur actuel ('black' ou 'red').
        :rtype: str
        """
        return self.current_player

    def get_phase(self):
        """
        Retourne la phase actuelle du jeu.

        :param self: L'instance de l'objet.
        :return: La phase de jeu en cours ('drop' or 'move').
        :rtype: str
        """
        return self.phase

    def get_turn_count(self):
        """
        Retourne le nombre de tours écoulés.

        :param self: L'instance de l'objet.
        :return: Le nombre total de tours joués.
        :rtype: int
        """
        return self.turn_count

    def get_winner(self):
        """
        Retourne le gagnant du jeu, s'il y en a un.

        :param self: L'instance de l'objet.
        :return: La couleur du gagnant ('black' ou 'red'), ou None s'il n'y a pas encore de gagnant.
        :rtype: str or None
        """
        return self.winner

    def is_valid_position(self, position):
        """
        Vérifie si une position est valide sur le plateau.

        Une position est valide si elle est comprise entre 0 et 24.

        :param self: L'instance de l'objet.
        :param position: L'index de la case à vérifier.
        :type position: int
        :return: True si la position est valide, False sinon.
        :rtype: bool
        """
        return 0 <= position < 25

    def is_position_free(self, position):
        """
        Vérifie si une position est libre sur le plateau.

        :param self: L'instance de l'objet.
        :param position: L'index de la case à vérifier.
        :type position: int
        :return: True si la case est libre (contient None), False sinon.
        :rtype: bool
        """
        return self.board[position] is None
    
    def is_game_over(self):
        """
        Vérifie si le jeu est terminé.

        Le jeu est considéré comme terminé si un gagnant a été désigné.

        :param self: L'instance de l'objet.
        :return: True si la partie est terminée, False sinon.
        :rtype: bool
        """
        return self.winner is not None

    def drop_piece(self, position):
        """
        Place un pion sur le plateau pendant la phase de placement ('drop').

        Vérifie la validité du coup, met à jour le plateau, le compteur de tours
        et vérifie une condition de victoire. Passe à la phase 'move' si 8 pions
        sont posés.

        :param self: L'instance de l'objet.
        :param position: La case où poser le pion.
        :type position: int
        :return: True si le pion a été placé, False si le coup est invalide.
        :rtype: bool
        """
        if not self.is_valid_position(position) or not self.is_position_free(position) or self.phase != 'drop' or self.winner is not None:
            return False

        self.board[position] = self.current_player
        self.turn_count += 1

        # Vérifie si le joueur actuel a gagné
        if self.check_win(self.current_player):
            self.winner = self.current_player
            return True

        # Change de joueur
        self.switch_player()

        # Vérifie si la phase de placement est terminée
        if self.turn_count >= 8:
            self.phase = 'move'

        return True

    def move_piece(self, from_position, to_position):
        """
        Déplace un pion sur le plateau pendant la phase de mouvement ('move').

        Vérifie la validité du déplacement (pion du joueur, case adjacente libre),
        effectue le mouvement et vérifie une condition de victoire.

        :param self: L'instance de l'objet.
        :param from_position: La position de départ du pion.
        :type from_position: int
        :param to_position: La position d'arrivée du pion.
        :type to_position: int
        :return: True si le déplacement a réussi, False si le coup est invalide.
        :rtype: bool
        """
        if self.phase != 'move' or self.winner is not None:
            return False

        if not (self.is_valid_position(from_position) and self.is_valid_position(to_position)):
            return False

        if self.board[from_position] != self.current_player or not self.is_position_free(to_position):
            return False

        # Vérifie si le déplacement est vers une position adjacente
        if abs(from_position - to_position) not in [1, 5, 6, 4]:
            return False

        # Déplace le pion
        self.board[from_position] = None
        self.board[to_position] = self.current_player

        # Vérifie si le joueur actuel a gagné
        if self.check_win(self.current_player):
            self.winner = self.current_player
            return True

        # Change de joueur
        self.switch_player()

        return True

    def switch_player(self):
        """
        Change le joueur actuel.

        Passe de 'black' à 'red' et vice-versa.

        :param self: L'instance de l'objet.
        :return: Aucun.
        """
        self.current_player = 'red' if self.current_player == 'black' else 'black'

    def generate_win_patterns(self):
        """
        Génère et retourne toutes les configurations gagnantes possibles.

        Calcule les alignements horizontaux, verticaux, diagonaux et les carrés 2x2
        de 4 pions qui constituent une victoire.

        :param self: L'instance de l'objet.
        :return: Une liste de listes, où chaque sous-liste est une combinaison de 
                 4 positions gagnantes.
        :rtype: list[list[int]]
        """
        win_patterns = []

        # Alignements horizontaux
        for row in range(5):
            for col in range(2):
                pattern = [row * 5 + col + i for i in range(4)]
                win_patterns.append(pattern)

        # Alignements verticaux
        for row in range(2):
            for col in range(5):
                pattern = [row * 5 + col + i * 5 for i in range(4)]
                win_patterns.append(pattern)

        # Alignements diagonaux (de haut-gauche à bas-droite)
        for row in range(2):
            for col in range(2):
                pattern = [row * 5 + col + i * 6 for i in range(4)]
                win_patterns.append(pattern)

        # Alignements diagonaux (de haut-droite à bas-gauche)
        for row in range(2):
            for col in range(3, 5):
                pattern = [row * 5 + col + i * 4 for i in range(4)]
                win_patterns.append(pattern)

        # Carrés 2x2
        for row in range(4):
            for col in range(4):
                pattern = [row * 5 + col, row * 5 + col + 1,
                           (row + 1) * 5 + col, (row + 1) * 5 + col + 1]
                win_patterns.append(pattern)
        return win_patterns

    def check_win(self, player):
        """
        Vérifie si un joueur donné a gagné.

        Parcourt toutes les configurations gagnantes et vérifie si le joueur
        occupe toutes les positions de l'une d'entre elles.

        :param self: L'instance de l'objet.
        :param player: Le joueur à vérifier ('black' ou 'red').
        :type player: str
        :return: True si le joueur a gagné, False sinon.
        :rtype: bool
        """
        # Vérifie toutes les lignes et tous les carrés possibles
        win_patterns = self.win_patterns

        for pattern in win_patterns:
            if all(self.board[pos] == player for pos in pattern):
                return True

        return False
