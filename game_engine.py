# Let's create a Python class to represent the Teeko game engine.

class TeekoGame:
    def __init__(self):
        """Initialize the Teeko game with an empty board and game state."""
        self.board = [None] * 25  # 5x5 board represented as a list
        self.current_player = 'black'  # Black starts first
        self.phase = 'drop'  # Game starts in the drop phase
        self.turn_count = 0
        self.winner = None
        self.win_patterns = self.generate_win_patterns()
        
    def reset(self):
        """Reset the game to the initial state."""
        self.board = [None] * 25
        self.current_player = 'black'
        self.phase = 'drop'
        self.turn_count = 0
        self.winner = None
        
    def get_board(self):
        """Return the current state of the board."""
        return self.board

    def get_current_player(self):
        """Return the current player."""
        return self.current_player

    def get_phase(self):
        """Return the current phase of the game."""
        return self.phase

    def get_turn_count(self):
        """Return the current turn count."""
        return self.turn_count

    def get_winner(self):
        """Return the winner of the game, if any."""
        return self.winner

    def is_valid_position(self, position):
        """Check if the position is valid on the board."""
        return 0 <= position < 25

    def is_position_free(self, position):
        """Check if the position is free on the board."""
        return self.board[position] is None
    
    def is_game_over(self):
        """Check if the game is over."""
        return self.winner is not None

    def drop_piece(self, position):
        """Drop a piece on the board during the drop phase."""
        if not self.is_valid_position(position) or not self.is_position_free(position) or self.phase != 'drop' or self.winner is not None:
            return False

        self.board[position] = self.current_player
        self.turn_count += 1

        # Check if the current player has won
        if self.check_win(self.current_player):
            self.winner = self.current_player
            return True

        # Switch player
        self.switch_player()

        # Check if the drop phase is over
        if self.turn_count >= 8:
            self.phase = 'move'

        return True

    def move_piece(self, from_position, to_position):
        """Move a piece on the board during the move phase."""
        if self.phase != 'move' or self.winner is not None:
            return False

        if not (self.is_valid_position(from_position) and self.is_valid_position(to_position)):
            return False

        if self.board[from_position] != self.current_player or not self.is_position_free(to_position):
            return False

        # Check if the move is to an adjacent position
        if abs(from_position - to_position) not in [1, 5, 6, 4]:
            return False

        # Move the piece
        self.board[from_position] = None
        self.board[to_position] = self.current_player

        # Check if the current player has won
        if self.check_win(self.current_player):
            self.winner = self.current_player
            return True

        # Switch player
        self.switch_player()

        return True

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 'red' if self.current_player == 'black' else 'black'

    def generate_win_patterns(self):
        """Génère automatiquement les configurations gagnantes."""
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
        """Check if the player has won by forming a line or a square."""
        # Check all possible lines and squares
        win_patterns = self.win_patterns

        for pattern in win_patterns:
            if all(self.board[pos] == player for pos in pattern):
                return True

        return False

# Example usage:
# game = TeekoGame()
# game.drop_piece(0)  # Black drops a piece at position 0
# game.drop_piece(1)  # red drops a piece at position 1
# game.move_piece(from_position, to_position)  # Move a piece during the move phase

TeekoGame