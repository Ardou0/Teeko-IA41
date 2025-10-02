from game_engine import TeekoGame
from ai_template import TeekoAI

def main():
    # Créer une instance du jeu
    game = TeekoGame()
    ai1 = TeekoAI(game, "black", 1)
    ai2 = TeekoAI(game, "white", "teacher")
    print("Jeu Teeko initialisé.")
    while game.get_winner() is None:
        ai1.make_move()
        ai2.last_opponent_move = ai1.last_move
        ai2.make_move()
        ai1.last_opponent_move = ai2.last_move
    if game.get_winner() == "black":
        print(f"Le gagnant est: Ai1")
    if game.get_winner() == "white":
        print(f"Le gagnant est: Ai2")
    print(game.get_board())  # Afficher l'état actuel du plateau

if __name__ == "__main__":
    main()
