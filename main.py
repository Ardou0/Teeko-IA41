# from game_engine import TeekoGame
# from ai_template import TeekoAI
# #from ai_agent import TeekoRLAgent

# def main():
#     # Créer une instance du jeu
#     game = TeekoGame()
#     ai1 = TeekoAI(game, "black", 1)
#     ai2 = TeekoAI(game, "white", "teacher")
#     print("Jeu Teeko initialisé.")
#     while game.get_winner() is None:
#         ai1.make_move()
#         ai2.last_opponent_move = ai1.last_move
#         ai2.make_move()
#         ai1.last_opponent_move = ai2.last_move
#     if game.get_winner() == "black":
#         print(f"Le gagnant est: Ai1 (pionts noirs)")
#     if game.get_winner() == "white":
#         print(f"Le gagnant est: Ai2 (pionts blancs)")
#     print(game.get_board())  # Afficher l'état actuel du plateau




# if __name__ == "__main__":
#     main() 


from interface import App
import tkinter as tk

if __name__ == "__main__":
    # App().mainloop()
    print("Début de l'application...")
    try:
        app = App()
        print("App créée avec succès")
        app.mainloop()
    except Exception as e:
        print(f"Erreur : {e}")
        import traceback
        traceback.print_exc()