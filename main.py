from game_engine import TeekoGame

def main():
    # Créer une instance du jeu
    game = TeekoGame()

    # Exemple de pose de pions
    game.drop_piece(0)  
    print(f"Plateau après le premier tour : {game.get_board()}")
    print(f"Joueur actuel : {game.get_current_player()}")

    game.drop_piece(2) 
    print(f"Plateau après le deuxième tour : {game.get_board()}")
    print(f"Joueur actuel : {game.get_current_player()}")
    game.drop_piece(1)     
    game.drop_piece(3)      
    game.drop_piece(5)     
    game.drop_piece(7) 
    game.drop_piece(8)     
    game.drop_piece(8) # Essayer de poser sur une position occupée (devrait échouer)
    
    # game.move_piece(from_position=0, to_position=1) 
    # Afficher l'état du jeu
    print(f"Phase actuelle : {game.get_phase()}")
    print(f"Nombre de tours joués : {game.get_turn_count()}")
    print(f"Gagnant actuel : {game.get_winner()}")

if __name__ == "__main__":
    main()
