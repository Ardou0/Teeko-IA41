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
        self.ai_white = None
        self.last_winner = None

    def show(self, name):
        self.screens[name].tkraise()

    def new_game(self, options):
        # options: dict('mode', 'who_starts', 'white_level')
        self.game = TeekoGame()
        self.ai_black = None
        self.ai_white = None
        # Instanciation IA selon options
        mode = options["mode"]
        who_starts = options["who_starts"]
        white_level = options["white_level"]
        # Noir = humain par défaut dans HvIA
        if mode == "Humain vs IA":
            self.ai_white = TeekoAI(self.game, "white", white_level)
        elif mode == "IA vs IA":
            # Exemple: noir teacher, blanc standard configurable si besoin
            self.ai_black = TeekoAI(self.game, "black", "teacher" if options["black_level"] == "teacher" else 1)
            self.ai_white = TeekoAI(self.game, "white", "teacher" if options["white_level"] == "teacher" else 1)
        elif mode == "Humain vs Humain":
            pass

        # Forcer le starter si différent de ‘black’
        if who_starts == "white" and self.game.get_current_player() != "white":
            self.game.switch_player()

        # Lancer l’écran de jeu
        game_screen: GameScreen = self.screens["GameScreen"]
        game_screen.bind_runtime(self.game, self.ai_black, self.ai_white, options)
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
        tk.OptionMenu(self, self.who_starts, "black", "white").pack(pady=4)

        # Niveaux IA
        self.white_level = tk.StringVar(value="teacher")
        self.black_level = tk.StringVar(value="teacher")
        self.white_box = tk.Frame(self)
        self.black_box = tk.Frame(self)
        tk.Label(self.white_box, text="Niveau IA blanche").pack(side="left")
        tk.OptionMenu(self.white_box, self.white_level, "standard", "teacher").pack(side="left")
        self.white_box.pack(pady=4)

        tk.Label(self.black_box, text="Niveau IA noire").pack(side="left")
        tk.OptionMenu(self.black_box, self.black_level, "standard", "teacher").pack(side="left")
        self.black_box.pack(pady=4)

        # Met à jour la visibilité des options selon le mode
        def refresh_visibility(*_):
            if self.mode.get() == "Humain vs IA":
                self.white_box.pack(pady=4)
                self.black_box.pack_forget()
            elif self.mode.get() == "IA vs IA":
                self.white_box.pack(pady=4)
                self.black_box.pack(pady=4)
            else:
                self.white_box.pack_forget()
                self.black_box.pack_forget()
        self.mode.trace_add("write", refresh_visibility)
        refresh_visibility()

        tk.Button(self, text="Lancer la partie", command=self.launch).pack(pady=16)

    def launch(self):
        options = {
            "mode": self.mode.get(),
            "who_starts": self.who_starts.get(),
            "white_level": self.white_level.get(),
            "black_level": self.black_level.get(),
        }
        self.app.new_game(options)

class GameScreen(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.game = None
        self.ai_black = None
        self.ai_white = None
        self.options = None
        self.selected_from = None

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

    def bind_runtime(self, game, ai_black, ai_white, options):
        self.game = game
        self.ai_black = ai_black
        self.ai_white = ai_white
        self.options = options
        self.selected_from = None
        self.refresh()

    def kickoff_if_ai(self):
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "white" and self.ai_white):
                self.after(400, self.ai_turn)

    def on_click(self, r, c):
        if self.game is None or self.game.is_game_over():
            return
        cur = self.game.get_current_player()
        # Bloquer si c'est au tour de l'IA
        if (cur == "black" and self.ai_black) or (cur == "white" and self.ai_white):
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

    def post_move_flow(self):
        if self.game.get_winner():
            self.finish()
        else:
            self.after(400, self.ai_turn)

    def ai_turn(self):
        if self.game is None or self.game.is_game_over():
            return
        cur = self.game.get_current_player()
        ai = self.ai_white if cur == "white" else self.ai_black
        if ai:
            ai.make_move()
            self.refresh()
            if self.game.get_winner():
                self.finish()

    def finish(self):
        winner = self.game.get_winner()
        self.app.finish_game(winner)

    def abort(self):
        # Retour au menu de départ
        self.app.show("StartScreen")

    def refresh(self):
        board = self.game.get_board() if self.game else [None]*25
        for i in range(5):
            for j in range(5):
                v = board[i*5 + j]
                self.buttons[i][j].config(text=("⚫" if v == "black" else ("⚪" if v == "white" else "")))
        if self.game and not self.game.is_game_over():
            cur = self.game.get_current_player()
            if (cur == "black" and self.ai_black) or (cur == "white" and self.ai_white):
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
        nom = {"black": "Noir", "white": "Blanc"}.get(winner, str(winner))
        self.label.config(text=f"Gagnant : {nom}")

    def back_to_menu(self):
        self.app.show("StartScreen")

if __name__ == "__main__":
    App().mainloop()
