# Let's create a Python class to represent the Teeko game engine.

class TeekoGame:
    def __init__(self):
        """Initialize the Teeko game with an empty board and game state."""
        self.board = [None] * 25  # 5x5 board represented as a list
        self.current_player = 'black'  # Black starts first
        self.phase = 'drop'  # Game starts in the drop phase
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
        self.current_player = 'white' if self.current_player == 'black' else 'black'

    def check_win(self, player):
        """Check if the player has won by forming a line or a square."""
        # Check all possible lines and squares
        win_patterns = [
            # Horizontal lines
            [0, 1, 2, 3], [1, 2, 3, 4],
            [5, 6, 7, 8], [6, 7, 8, 9],
            [10, 11, 12, 13], [11, 12, 13, 14],
            [15, 16, 17, 18], [16, 17, 18, 19],
            [20, 21, 22, 23], [21, 22, 23, 24],
            
            # Vertical lines
            [0, 5, 10, 15], [5, 10, 15, 20],
            [1, 6, 11, 16], [6, 11, 16, 21],
            [2, 7, 12, 17], [7, 12, 17, 22],
            [3, 8, 13, 18], [8, 13, 18, 23],
            [4, 9, 14, 19], [9, 14, 19, 24],
            
            # Diagonal lines
            [0, 6, 12, 18], [6, 12, 18, 24],
            [1, 7, 13, 19], [5, 11, 17, 23],
            
            # Squares
            [0, 1, 5, 6], [1, 2, 6, 7], [2, 3, 7, 8], [3, 4, 8, 9],
            [5, 6, 10, 11], [6, 7, 11, 12], [7, 8, 12, 13], [8, 9, 13, 14],
            [10, 11, 15, 16], [11, 12, 16, 17], [12, 13, 17, 18], [13, 14, 18, 19],
            [15, 16, 20, 21], [16, 17, 21, 22], [17, 18, 22, 23], [18, 19, 23, 24]
        ]

        for pattern in win_patterns:
            if all(self.board[pos] == player for pos in pattern):
                return True

        return False

# Example usage:
# game = TeekoGame()
# game.drop_piece(0)  # Black drops a piece at position 0
# game.drop_piece(1)  # White drops a piece at position 1
# game.move_piece(from_position, to_position)  # Move a piece during the move phase

TeekoGame