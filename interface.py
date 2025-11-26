import tkinter as tk
from game_engine import TeekoGame
from ai_template import TeekoAI

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teeko")
        self.geometry("385x600")
        self.configure(bg="#FFEEE0")
        self.container = tk.Frame(self, bg = "#FFEEE0")
        self.container.pack(fill="both", expand=True)
        self.screens = {}
        for Screen in (StartScreen, GameScreen):
            frame = Screen(self.container, self)
            self.screens[Screen.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show("StartScreen")

        # État partagé entre écrans
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.last_winner = None

    def show(self, name):
        self.screens[name].tkraise()

    def new_game(self, options):
        self.game = TeekoGame()
        self.ai_black = None
        self.ai_red = None
        
        # Conversion des niveaux texte → profondeur
        level_to_depth = {
            "Débutant": 1,
            "Normal": 2, 
            "Pro": 4,
            "Expert": 5
        }
        
        mode = options["mode"]
        who_starts = options["who_starts"]

        # Conversion "Noir"/"Rouge" en "black"/"red"
        who_starts_color = "black" if who_starts == "Noir" else "red"
        
        # Instanciation des IA avec les bons niveaux
        if mode == "Humain vs IA":
            depth = level_to_depth[options["red_level"]]
            self.ai_red = TeekoAI(self.game, "red", depth)
        elif mode == "IA vs IA":
            depth_black = level_to_depth[options["black_level"]]
            depth_red = level_to_depth[options["red_level"]]
            self.ai_black = TeekoAI(self.game, "black", depth_black)
            self.ai_red = TeekoAI(self.game, "red", depth_red)
        elif mode == "Humain vs Humain":
            pass

        # Forcer le starter si différent de 'black'
        if who_starts_color == "red" and self.game.get_current_player() != "red":
            self.game.switch_player()

        # Lancer l'écran de jeu
        game_screen: GameScreen = self.screens["GameScreen"]
        game_screen.bind_runtime(self.game, self.ai_black, self.ai_red, options)
        self.show("GameScreen")
        game_screen.kickoff_if_ai()

class StartScreen(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg = "#FFEEE0")
        self.app = app
        # Frame vide pour créer de l'espace en haut
        tk.Frame(self, height=20, bg="#FFEEE0").pack()
        tk.Label(self, text="Teeko - Choix du mode", font=("Helvetica", 16, "bold"), bg = "#FFEEE0").pack(pady=20)

        # Conteneur pour centrer tous les éléments
        self.main_container = tk.Frame(self, bg = "#FFEEE0")
        self.main_container.pack(pady = 20)

        # Mode de jeu
        self.mode = tk.StringVar(value="Humain vs IA")
        tk.Label(self, text="Mode de jeu", bg = "#FFEEE0", font=("Helvetica", 11, "bold")).pack()
        mode_menu = tk.OptionMenu(self, self.mode, "Humain vs IA", "IA vs IA", "Humain vs Humain")
        self.configure_option_menu(mode_menu)
        mode_menu.pack(pady=4)

        # Qui commence
        self.who_starts = tk.StringVar(value="Noir")
        tk.Label(self, text="Qui commence ?", bg = "#FFEEE0", font=("Helvetica", 11, "bold")).pack()
        who_menu = tk.OptionMenu(self, self.who_starts, "Noir", "Rouge")
        self.configure_option_menu(who_menu)
        who_menu.pack(pady=4)

        # Niveaux IA avec les nouveaux choix
        self.red_level = tk.StringVar(value="Normal")
        self.black_level = tk.StringVar(value="Normal")
        
        # Frame pour IA Rouge
        self.red_frame = tk.Frame(self, bg = "#FFEEE0")
        tk.Label(self.red_frame, text="Niveau IA rouge", bg = "#FFEEE0", font=("Helvetica", 11, "bold")).pack(side="left")
        # Ajout des nouveaux niveaux
        red_menu = tk.OptionMenu(self.red_frame, self.red_level, 
                     "Débutant", "Normal", "Pro", "Expert")
        self.configure_option_menu(red_menu)
        red_menu.pack(side="left")
        
        # Frame pour IA Noire  
        self.black_frame = tk.Frame(self, bg = "#FFEEE0")
        tk.Label(self.black_frame, text="Niveau IA noire", bg = "#FFEEE0",font=("Helvetica", 11, "bold")).pack(side="left")
        black_menu = tk.OptionMenu(self.black_frame, self.black_level, 
                     "Débutant", "Normal", "Pro", "Expert")
        black_menu.pack(side="left")
        self.configure_option_menu(black_menu)

        # # Bouton en dernier
        self.launch_btn = tk.Button(self, text="Lancer la partie", command=self.launch,
                                   bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                                   activeforeground="white", font=("Helvetica", 12, "bold"))
        self.launch_btn.pack(pady=16)

        # Configuration initiale
        self.refresh_display()
        self.mode.trace_add("write", lambda *_: self.refresh_display())

    def configure_option_menu(self, menu):
        """Configure complètement un OptionMenu."""
        menu.config(
            bg="#3E2D2D", 
            fg="white", 
            activebackground="#5A4444", 
            activeforeground="white",
            width=12,  # Largeur fixe pour uniformité
            font=("Helvetica", 10, "bold")
        )
        
        # Menu déroulant
        try:
            dropdown = menu.nametowidget(menu.menuname)
            dropdown.config(
                bg="#3E2D2D",
                fg="white", 
                activebackground="#5A4444",
                activeforeground="white",
                font=("Helvetica", 10, "bold")
            )
        except:
            pass  # Si ça ne fonctionne pas, on ignore

    def refresh_display(self):
        self.red_frame.pack_forget()
        self.black_frame.pack_forget()
        
        mode = self.mode.get()
        if mode == "Humain vs IA":
            self.red_frame.pack(pady=8, before=self.launch_btn)
        elif mode == "IA vs IA":
            self.red_frame.pack(pady=8, before=self.launch_btn)
            self.black_frame.pack(pady=8, before=self.launch_btn)

    def launch(self):
        options = {
            "mode": self.mode.get(),
            "who_starts": self.who_starts.get(),
            "red_level": self.red_level.get(),
            "black_level": self.black_level.get(),
        }
        self.app.new_game(options)

class GameScreen(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg="#FFEEE0") 
        self.app = app
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.options = None
        self.selected_from = None
        self.aborted = False  # Flag d'arrêt

        # Frame vide pour créer de l'espace en haut
        tk.Frame(self, height=20, bg="#FFEEE0").pack()

        self.status = tk.Label(self, text="Prêt", font=("Helvetica", 14, "bold"), bg = "#FFEEE0")
        self.status.pack(pady=8)

        self.move_count_label = tk.Label(self, text="Coups joués : 0", font=("Helvetica", 11), bg="#FFEEE0")
        self.move_count_label.pack()

        # Conteneur pour centrer le plateau
        self.center_container = tk.Frame(self, bg = "#FFEEE0")
        self.center_container.pack(expand=True, fill="both")
        
        # Plateau centrée
        self.board_frame = tk.Frame(self.center_container, bg="#E7BB66")
        self.board_frame.pack(anchor="center", pady=30)


        self.buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                b = tk.Button(self.board_frame, text="", width=5, height=2, font=("Helvetica", 14),
                              command=lambda r=i, c=j: self.on_click(r, c),
                              bg="#3E2D2D", fg="white", activebackground="#5A4444", relief="raised", bd=2)
                b.grid(row=i, column=j, padx = 6, pady = 6)
                row.append(b)
            self.buttons.append(row)

        tk.Button(self, text="Abandonner", command=self.abort,
                 bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                 activeforeground="white", font=("Helvetica", 12, "bold")).pack(pady=10)

    def bind_runtime(self, game, ai_black, ai_red, options):
        self.game = game
        self.ai_black = ai_black
        self.ai_red = ai_red
        self.options = options
        self.selected_from = None
        self.aborted = False
        self.move_count = 0
        
        # Supprimer TOUS les boutons existants
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or (isinstance(widget, tk.Frame) and any(isinstance(child, tk.Button) for child in widget.winfo_children())):
                widget.destroy()
        
        # Recréer le bouton Abandonner
        tk.Button(self, text="Abandonner", command=self.abort,
                bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                activeforeground="white", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        self.refresh()

    #Au début de partie va regarder si c'est le tour d'une ia et la faire jouer si c'est le cas
    def kickoff_if_ai(self):
        if self.aborted:
            return
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.after(400, self.ai_turn)

    def on_click(self, r, c):
        if self.game is None or self.game.is_game_over():
            return
        cur = self.game.get_current_player()
        # Bloquer si c'est au tour de l'IA
        if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
            return
        pos = r * 5 + c
        if self.game.get_phase() == "drop":
            if self.game.drop_piece(pos):
                # AFFICHER le coup humain
                print(f"Humain ({cur}) a joué: ('drop', {pos + 1})")
                self.post_move_flow()
        else:  # phase move
            if self.selected_from is None:
                if self.game.get_board()[pos] == cur:
                    self.selected_from = pos
                    self.status.config(text="Choisis la case d'arrivée")
            else:
                if self.game.move_piece(self.selected_from, pos):
                    # AFFICHER le coup humain
                    print(f"Humain ({cur}) a joué: ('move', {self.selected_from}, {pos + 1})")
                    self.selected_from = None
                    self.post_move_flow()
                else:
                    self.status.config(text="Coup invalide. Re-sélectionne.")
                    self.selected_from = None
        self.refresh()
        
    #Verifie si c'est au tour d'une ia de jouer après un coup humain
    def post_move_flow(self):
        self.move_count += 1
        if self.aborted:
            return
        if self.game.get_winner():
            self.finish()
        else:
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.after(400, self.ai_turn)

    def ai_turn(self):
        if self.aborted or self.game is None or self.game.is_game_over():
            return
        
        cur = self.game.get_current_player()
        ai = self.ai_red if cur == "red" else self.ai_black
        
        if ai:
            ai.make_move()
            self.move_count += 1
            self.refresh()
            if self.game.get_winner():
                self.finish()
            elif not self.game.is_game_over() and not self.aborted:
                next_player = self.game.get_current_player()
                if (next_player == "black" and self.ai_black) or (next_player == "red" and self.ai_red):
                    self.after(400, self.ai_turn)

    def finish(self):
        winner = self.game.get_winner()
        
        # Afficher le message de victoire dans l'interface
        nom = {"black": "Noir", "red": "Rouge"}.get(winner, str(winner))
        self.status.config(text=f"Partie terminée ! Gagnant : {nom}")
        
        # APPELER print_winner_info pour afficher dans la console
        self.print_winner_info(winner)
        
        # Supprimer TOUS les boutons existants
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()
        
        # Créer les boutons de fin (uniquement en fin de partie)
        button_frame = tk.Frame(self, bg="#FFEEE0")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Rejouer", command=self.replay, 
                font=("Helvetica", 12, "bold"), width=8,
                bg="#3E2D2D", fg="white", activebackground="#5A4444").pack(side="left", padx=10)
        
        tk.Button(button_frame, text="Quitter", command=self.app.destroy,
                font=("Helvetica", 12, "bold"), width=8,
                bg="#3E2D2D", fg="white", activebackground="#5A4444").pack(side="left", padx=10)
        
        self.refresh()

    def print_winner_info(self, winner):
        """Affiche dans la console le gagnant et la position des pions gagnants."""
        print("=" * 50)
        print(f"PARTIE TERMINÉE - GAGNANT : {winner.upper()}")
        print("=" * 50)
        
        board = self.game.get_board()
        win_patterns = self.game.win_patterns
        
        # Trouver le motif gagnant
        winning_pattern = None
        for pattern in win_patterns:
            if all(board[pos] == winner for pos in pattern):
                winning_pattern = pattern
                break
        
        if winning_pattern:
            print(f"Motif gagnant ({winner}) :")
            # Afficher les coordonnées des pions gagnants
            for pos in winning_pattern:
                row, col = divmod(pos, 5)
                print(f"  - Position {pos + 1} → Ligne {row + 1}, Colonne {col + 1}")
        else:
            print("Erreur : Impossible de trouver le motif gagnant")
        
        print("=" * 50)

    def replay(self):
        """Retourne au menu principal pour choisir une nouvelle configuration."""
        self.app.show("StartScreen")

    def abort(self):
        """Arrête la partie et retourne au menu."""
        print("Partie abandonnée")
        # Arrêter toutes les IA en cours
        self.aborted = True
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.options = None
        
        # Retour au menu de départ
        self.app.show("StartScreen")

    def refresh(self):
        board = self.game.get_board() if self.game else [None]*25
        for i in range(5):
            for j in range(5):
                v = board[i*5 + j]
                if v == "black":
                    self.buttons[i][j].config(text="⬤", fg="black", bg="#5A4444")
                elif v == "red":
                    self.buttons[i][j].config(text="⬤", fg="red", bg="#5A4444")
                else:
                    self.buttons[i][j].config(text="", bg="#5A4444")
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.status.config(text=f"Tour de l'IA ({cur})…")
            else:
                self.status.config(text=f"À toi ({cur}) — Phase {self.game.get_phase()}")
        
        if hasattr(self, 'move_count_label'):
            self.move_count_label.config(text=f"Coups joués : {self.move_count if hasattr(self, 'move_count') else 0}")