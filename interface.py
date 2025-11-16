import tkinter as tk
from game_engine import TeekoGame
from ai_template import TeekoAI

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teeko")
        self.geometry("420x520")
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.screens = {}
        for Screen in (StartScreen, GameScreen, EndScreen):
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
        if who_starts == "red" and self.game.get_current_player() != "red":
            self.game.switch_player()

        # Lancer l'écran de jeu
        game_screen: GameScreen = self.screens["GameScreen"]
        game_screen.bind_runtime(self.game, self.ai_black, self.ai_red, options)
        self.show("GameScreen")
        game_screen.kickoff_if_ai()

    def finish_game(self, winner):
        self.last_winner = winner
        end: EndScreen = self.screens["EndScreen"]
        end.set_winner(winner)
        self.show("EndScreen")

class StartScreen(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        tk.Label(self, text="Teeko - Choix du mode", font=("Arial", 16)).pack(pady=12)

        # Mode de jeu
        self.mode = tk.StringVar(value="Humain vs IA")
        tk.Label(self, text="Mode de jeu").pack()
        tk.OptionMenu(self, self.mode, "Humain vs IA", "IA vs IA", "Humain vs Humain").pack(pady=4)

        # Qui commence
        self.who_starts = tk.StringVar(value="black")
        tk.Label(self, text="Qui commence ?").pack()
        tk.OptionMenu(self, self.who_starts, "black", "red").pack(pady=4)

        # Niveaux IA avec les nouveaux choix
        self.red_level = tk.StringVar(value="Normal")
        self.black_level = tk.StringVar(value="Normal")
        
        # Frame pour IA Rouge
        self.red_frame = tk.Frame(self)
        tk.Label(self.red_frame, text="Niveau IA rouge").pack(side="left")
        # Ajout des nouveaux niveaux
        tk.OptionMenu(self.red_frame, self.red_level, 
                     "Débutant", "Normal", "Pro", "Expert").pack(side="left")
        
        # Frame pour IA Noire  
        self.black_frame = tk.Frame(self)
        tk.Label(self.black_frame, text="Niveau IA noire").pack(side="left")
        tk.OptionMenu(self.black_frame, self.black_level, 
                     "Débutant", "Normal", "Pro", "Expert").pack(side="left")

        # Bouton en dernier
        self.launch_btn = tk.Button(self, text="Lancer la partie", command=self.launch)
        self.launch_btn.pack(pady=16)

        # Configuration initiale
        self.refresh_display()
        self.mode.trace_add("write", lambda *_: self.refresh_display())

    def refresh_display(self):
        self.red_frame.pack_forget()
        self.black_frame.pack_forget()
        
        mode = self.mode.get()
        if mode == "Humain vs IA":
            self.red_frame.pack(pady=4, before=self.launch_btn)
        elif mode == "IA vs IA":
            self.red_frame.pack(pady=4, before=self.launch_btn)
            self.black_frame.pack(pady=4, before=self.launch_btn)

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
        super().__init__(parent)
        self.app = app
        self.game = None
        self.ai_black = None
        self.ai_red = None
        self.options = None
        self.selected_from = None
        self.aborted = False  # Flag d'arrêt

        self.status = tk.Label(self, text="Prêt", font=("Arial", 14))
        self.status.pack(pady=8)

        self.board_frame = tk.Frame(self)
        self.board_frame.pack()
        self.buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                b = tk.Button(self.board_frame, text="", width=4, height=2, font=("Arial", 14),
                              command=lambda r=i, c=j: self.on_click(r, c))
                b.grid(row=i, column=j)
                row.append(b)
            self.buttons.append(row)

        tk.Button(self, text="Abandonner", command=self.abort).pack(pady=10)

    def bind_runtime(self, game, ai_black, ai_red, options):
        self.game = game
        self.ai_black = ai_black
        self.ai_red = ai_red
        self.options = options
        self.selected_from = None
        self.aborted = False
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
                self.post_move_flow()
        else:  # phase move
            if self.selected_from is None:
                if self.game.get_board()[pos] == cur:
                    self.selected_from = pos
                    self.status.config(text="Choisis la case d'arrivée")
            else:
                if self.game.move_piece(self.selected_from, pos):
                    self.selected_from = None
                    self.post_move_flow()
                else:
                    self.status.config(text="Coup invalide. Re-sélectionne.")
                    self.selected_from = None
        self.refresh()
        
    #Verifie si c'est au tour d'une ia de jouer après un coup humain
    def post_move_flow(self):
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
            self.refresh()
            if self.game.get_winner():
                self.finish()
            elif not self.game.is_game_over() and not self.aborted:
                next_player = self.game.get_current_player()
                if (next_player == "black" and self.ai_black) or (next_player == "red" and self.ai_red):
                    self.after(400, self.ai_turn)

    def finish(self):
        winner = self.game.get_winner()
        self.app.finish_game(winner)

    def abort(self):
        """Arrête la partie et retourne au menu."""
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
                    self.buttons[i][j].config(text="●", fg="black", bg="white")
                elif v == "red":
                    self.buttons[i][j].config(text="●", fg="red", bg="white")
                else:
                    self.buttons[i][j].config(text="", bg="white")
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "red" and self.ai_red):
                self.status.config(text=f"Tour de l'IA ({cur})…")
            else:
                self.status.config(text=f"À toi ({cur}) — phase {self.game.get_phase()}")

class EndScreen(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.label = tk.Label(self, text="Fin de partie", font=("Arial", 18))
        self.label.pack(pady=16)
        tk.Button(self, text="Rejouer", command=self.back_to_menu).pack(pady=8)
        tk.Button(self, text="Quitter", command=self.app.destroy).pack(pady=8)

    def set_winner(self, winner):
        nom = {"black": "Noir", "red": "Rouge"}.get(winner, str(winner))
        self.label.config(text=f"Gagnant : {nom}")

    def back_to_menu(self):
        self.app.show("StartScreen")

if __name__ == "__main__":
    App().mainloop()
