import tkinter as tk
from game_engine import TeekoGame
from ai_template import TeekoAI

class App(tk.Tk):
    """
    Classe principale de l'application, héritant de tk.Tk.
    
    Cette classe agit comme le contrôleur central qui gère les différents écrans 
    (menu, jeu) et maintient l'état global de la partie (moteur de jeu, 
    instances des IA).
    """
    def __init__(self):
        """
        Initialise la fenêtre principale et les écrans de l'application.
        """
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

        # État partagé entre les différents écrans de l'application
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.last_winner = None

    def show(self, name):
        """
        Affiche un écran spécifique au premier plan.

        :param name: Le nom de la classe de l'écran à afficher.
        :type name: str
        """
        self.screens[name].tkraise()

    def new_game(self, options):
        """
        Configure et lance une nouvelle partie en fonction des options choisies.

        Cette méthode initialise le moteur de jeu, configure les joueurs (humains 
        ou IA avec le niveau de difficulté approprié) et bascule l'affichage 
        vers l'écran de jeu.

        :param options: Un dictionnaire contenant la configuration de la partie
                        (mode, niveaux des IA, etc.).
        :type options: dict
        """
        self.game = TeekoGame()
        self.ai_black = None
        self.ai_red = None
        
        level_to_depth = {
            "Débutant": 1, "Normal": 2, "Pro": 4, "Expert": 5
        }
        
        mode = options["mode"]
        who_starts_color = "black" if options["who_starts"] == "Noir" else "red"
        
        # Instanciation des IA en fonction du mode de jeu
        if mode == "Humain vs IA":
            depth = level_to_depth[options["red_level"]]
            self.ai_red = TeekoAI(self.game, "red", depth)
        elif mode == "IA vs IA":
            depth_black = level_to_depth[options["black_level"]]
            depth_red = level_to_depth[options["red_level"]]
            self.ai_black = TeekoAI(self.game, "black", depth_black)
            self.ai_red = TeekoAI(self.game, "red", depth_red)

        # Ajustement du joueur de départ si nécessaire
        if who_starts_color != self.game.get_current_player():
            self.game.switch_player()

        # Initialisation et affichage de l'écran de jeu
        game_screen = self.screens["GameScreen"]
        game_screen.bind_runtime(self.game, self.ai_black, self.ai_red, options)
        self.show("GameScreen")
        game_screen.kickoff_if_ai()

class StartScreen(tk.Frame):
    """
    Écran d'accueil et de configuration de la partie.
    
    Permet à l'utilisateur de choisir le mode de jeu, le niveau de difficulté 
    des IA et le joueur qui commence la partie.
    """
    def __init__(self, parent, app: App):
        """
        Initialise les widgets de l'écran de démarrage.

        :param parent: Le conteneur parent (Frame).
        :param app: L'instance principale de l'application App.
        """
        super().__init__(parent, bg = "#FFEEE0")
        self.app = app
        
        tk.Frame(self, height=20, bg="#FFEEE0").pack()
        tk.Label(self, text="Teeko - Choix du mode", font=("Helvetica", 16, "bold"), bg="#FFEEE0").pack(pady=20)

        self.main_container = tk.Frame(self, bg="#FFEEE0")
        self.main_container.pack(pady=20)

        # Widget pour le mode de jeu
        self.mode = tk.StringVar(value="Humain vs IA")
        tk.Label(self, text="Mode de jeu", bg="#FFEEE0", font=("Helvetica", 11, "bold")).pack()
        mode_menu = tk.OptionMenu(self, self.mode, "Humain vs IA", "IA vs IA", "Humain vs Humain")
        self.configure_option_menu(mode_menu)
        mode_menu.pack(pady=4)

        # Widget pour le joueur de départ
        self.who_starts = tk.StringVar(value="Noir")
        tk.Label(self, text="Qui commence ?", bg="#FFEEE0", font=("Helvetica", 11, "bold")).pack()
        who_menu = tk.OptionMenu(self, self.who_starts, "Noir", "Rouge")
        self.configure_option_menu(who_menu)
        who_menu.pack(pady=4)

        # Widgets pour le niveau des IA
        self.red_level = tk.StringVar(value="Normal")
        self.black_level = tk.StringVar(value="Normal")
        
        self.red_frame = tk.Frame(self, bg = "#FFEEE0")
        tk.Label(self.red_frame, text="Niveau IA rouge", bg="#FFEEE0", font=("Helvetica", 11, "bold")).pack(side="left")
        red_menu = tk.OptionMenu(self.red_frame, self.red_level, "Débutant", "Normal", "Pro", "Expert")
        self.configure_option_menu(red_menu)
        red_menu.pack(side="left")
        
        self.black_frame = tk.Frame(self, bg = "#FFEEE0")
        tk.Label(self.black_frame, text="Niveau IA noire", bg="#FFEEE0", font=("Helvetica", 11, "bold")).pack(side="left")
        black_menu = tk.OptionMenu(self.black_frame, self.black_level, "Débutant", "Normal", "Pro", "Expert")
        self.configure_option_menu(black_menu)
        black_menu.pack(side="left")

        # Bouton de lancement
        self.launch_btn = tk.Button(self, text="Lancer la partie", command=self.launch,
                                   bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                                   activeforeground="white", font=("Helvetica", 12, "bold"))
        self.launch_btn.pack(pady=16)

        self.refresh_display()
        self.mode.trace_add("write", lambda *_: self.refresh_display())

    def configure_option_menu(self, menu):
        """
        Applique un style uniforme aux widgets OptionMenu.

        :param menu: Le widget OptionMenu à configurer.
        :type menu: tk.OptionMenu
        """
        menu.config(
            bg="#3E2D2D", fg="white", activebackground="#5A4444", 
            activeforeground="white", width=12, font=("Helvetica", 10, "bold")
        )
        try:
            # Configuration du menu déroulant lui-même
            dropdown = menu.nametowidget(menu.menuname)
            dropdown.config(
                bg="#3E2D2D", fg="white", activebackground="#5A4444",
                activeforeground="white", font=("Helvetica", 10, "bold")
            )
        except tk.TclError:
            pass # Ignorer si le widget n'existe pas encore

    def refresh_display(self):
        """
        Affiche ou masque les menus de sélection de niveau d'IA en fonction
        du mode de jeu sélectionné.
        """
        self.red_frame.pack_forget()
        self.black_frame.pack_forget()
        
        mode = self.mode.get()
        if mode == "Humain vs IA":
            self.red_frame.pack(pady=8, before=self.launch_btn)
        elif mode == "IA vs IA":
            self.red_frame.pack(pady=8, before=self.launch_btn)
            self.black_frame.pack(pady=8, before=self.launch_btn)

    def launch(self):
        """
        Récupère les options sélectionnées par l'utilisateur et demande
        à l'application principale de lancer la partie.
        """
        options = {
            "mode": self.mode.get(),
            "who_starts": self.who_starts.get(),
            "red_level": self.red_level.get(),
            "black_level": self.black_level.get(),
        }
        self.app.new_game(options)

class GameScreen(tk.Frame):
    """
    Écran principal où se déroule la partie de Teeko.
    
    Cette classe gère l'affichage du plateau, les interactions de l'utilisateur,
    le déroulement des tours de jeu (humain et IA) et l'affichage de l'état
    de la partie.
    """
    def __init__(self, parent, app: App):
        """
        Initialise les widgets de l'écran de jeu.

        :param parent: Le conteneur parent (Frame).
        :param app: L'instance principale de l'application App.
        """
        super().__init__(parent, bg="#FFEEE0") 
        self.app = app
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.options = None
        self.selected_from = None
        self.aborted = False

        tk.Frame(self, height=20, bg="#FFEEE0").pack()
        self.status = tk.Label(self, text="Prêt", font=("Helvetica", 14, "bold"), bg="#FFEEE0")
        self.status.pack(pady=8)
        self.move_count_label = tk.Label(self, text="Coups joués : 0", font=("Helvetica", 11), bg="#FFEEE0")
        self.move_count_label.pack()

        self.center_container = tk.Frame(self, bg="#FFEEE0")
        self.center_container.pack(expand=True, fill="both")
        
        self.board_frame = tk.Frame(self.center_container, bg="#E7BB66")
        self.board_frame.pack(anchor="center", pady=30)

        self.buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                b = tk.Button(self.board_frame, text="", width=5, height=2, font=("Helvetica", 14),
                              command=lambda r=i, c=j: self.on_click(r, c),
                              bg="#3E2D2D", fg="white", activebackground="#5A4444", relief="raised", bd=2)
                b.grid(row=i, column=j, padx=6, pady=6)
                row.append(b)
            self.buttons.append(row)

        tk.Button(self, text="Abandonner", command=self.abort,
                 bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                 activeforeground="white", font=("Helvetica", 12, "bold")).pack(pady=10)

    def bind_runtime(self, game, ai_black, ai_red, options):
        """
        Associe une instance de jeu active et ses joueurs à cet écran.

        Cette méthode réinitialise l'état de l'écran pour une nouvelle partie.

        :param game: L'instance du moteur de jeu TeekoGame.
        :param ai_black: L'instance de l'IA pour le joueur noir, ou None.
        :param ai_red: L'instance de l'IA pour le joueur rouge, ou None.
        :param options: Le dictionnaire d'options de la partie.
        """
        self.game = game
        self.ai_black = ai_black
        self.ai_red = ai_red
        self.options = options
        self.selected_from = None
        self.aborted = False
        self.move_count = 0
        
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) or (isinstance(widget, tk.Frame) and any(isinstance(child, tk.Button) for child in widget.winfo_children())):
                widget.destroy()
        
        tk.Button(self, text="Abandonner", command=self.abort,
                bg="#3E2D2D", fg="white", activebackground="#5A4444", 
                activeforeground="white", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        self.refresh()

    def kickoff_if_ai(self):
        """
        Déclenche le premier tour si c'est à une IA de commencer.
        """
        if self.aborted: return
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.after(400, self.ai_turn)

    def on_click(self, r, c):
        """
        Gère les clics de l'utilisateur sur le plateau de jeu.

        La méthode gère la logique de placement ('drop') et de déplacement ('move')
        des pions pour un joueur humain.

        :param r: L'indice de la ligne cliquée (0-4).
        :type r: int
        :param c: L'indice de la colonne cliquée (0-4).
        :type c: int
        """
        if self.game is None or self.game.is_game_over(): return
        
        cur = self.game.get_current_player()
        is_ai_turn = (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red)
        if is_ai_turn: return

        pos = r * 5 + c
        if self.game.get_phase() == "drop":
            if self.game.drop_piece(pos):
                print(f"Humain ({cur}) a joué: ('drop', {pos + 1})")
                self.post_move_flow()
        else:
            if self.selected_from is None:
                if self.game.get_board()[pos] == cur:
                    self.selected_from = pos
                    self.status.config(text="Choisis la case d'arrivée")
            else:
                if self.game.move_piece(self.selected_from, pos):
                    print(f"Humain ({cur}) a joué: ('move', {self.selected_from + 1}, {pos + 1})")
                    self.selected_from = None
                    self.post_move_flow()
                else:
                    self.status.config(text="Coup invalide. Re-sélectionne.")
                    self.selected_from = None
        self.refresh()
        
    def post_move_flow(self):
        """
        Exécute la logique post-coup (mise à jour du compteur, vérification
        de fin de partie, passage de main à l'IA).
        """
        self.move_count += 1
        if self.aborted: return
        
        if self.game.get_winner():
            self.finish()
        else:
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.after(400, self.ai_turn)

    def ai_turn(self):
        """
        Exécute le tour de jeu pour une IA. 
        
        Identifie l'IA active, lui demande de jouer son coup, met à jour l'interface
        et gère la suite de la partie.
        """
        if self.aborted or self.game is None or self.game.is_game_over(): return
        
        cur = self.game.get_current_player()
        ai = self.ai_red if cur == "red" else self.ai_black
        
        if ai:
            ai.make_move()
            self.move_count += 1
            self.refresh()
            if self.game.get_winner():
                self.finish()
            elif not self.aborted:
                next_player = self.game.get_current_player()
                is_next_player_ai = (next_player == "black" and self.ai_black) or \
                                    (next_player == "red" and self.ai_red)
                if is_next_player_ai:
                    self.after(400, self.ai_turn)

    def finish(self):
        """
        Gère la fin de la partie. 
        
        Affiche le gagnant et propose les options "Rejouer" ou "Quitter".
        """
        winner = self.game.get_winner()
        nom = {"black": "Noir", "red": "Rouge"}.get(winner, str(winner))
        self.status.config(text=f"Partie terminée ! Gagnant : {nom}")
        
        self.print_winner_info(winner)
        
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button): widget.destroy()
        
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
        """
        Affiche des informations détaillées sur la victoire dans la console.

        :param winner: La couleur du joueur gagnant.
        :type winner: str
        """
        print("=" * 50)
        print(f"PARTIE TERMINÉE - GAGNANT : {winner.upper()}")
        print("=" * 50)
        
        board = self.game.get_board()
        winning_pattern = None
        for pattern in self.game.win_patterns:
            if all(board[pos] == winner for pos in pattern):
                winning_pattern = pattern
                break
        
        if winning_pattern:
            print(f"Motif gagnant ({winner}) :")
            for pos in winning_pattern:
                row, col = divmod(pos, 5)
                print(f"  - Position {pos + 1} → Ligne {row + 1}, Colonne {col + 1}")
        else:
            print("Erreur : Impossible de trouver le motif gagnant")
        print("=" * 50)

    def replay(self):
        """
        Retourne à l'écran d'accueil pour une nouvelle partie.
        """
        self.app.show("StartScreen")

    def abort(self):
        """
        Interrompt la partie en cours et retourne à l'écran d'accueil.
        """
        print("Partie abandonnée")
        self.aborted = True
        self.game = self.ai_black = self.ai_red = self.options = None
        self.app.show("StartScreen")

    def refresh(self):
        """
        Met à jour l'intégralité de l'interface graphique (plateau, labels)
        pour refléter l'état actuel du jeu.
        """
        board = self.game.get_board() if self.game else [None]*25
        for i in range(5):
            for j in range(5):
                piece = board[i*5 + j]
                color = "black" if piece == "black" else "red"
                text = "⬤" if piece else ""
                self.buttons[i][j].config(text=text, fg=color, bg="#5A4444")

        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.status.config(text=f"Tour de l'IA ({cur})…")
            else:
                self.status.config(text=f"À toi ({cur}) — Phase {self.game.get_phase()}")
        
        if hasattr(self, 'move_count_label'):
            self.move_count_label.config(text=f"Coups joués : {self.move_count if hasattr(self, 'move_count') else 0}")
