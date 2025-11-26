from interface import App
import tkinter as tk
def main():
    print("Début de l'application...")
    try:
        app = App()
        print("App créée avec succès")
        app.mainloop()
    except Exception as e:
        print(f"Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 