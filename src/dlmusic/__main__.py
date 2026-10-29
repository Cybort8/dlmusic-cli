import sys

from .cli import main_cli


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        sys.argv.pop(1)
        sys.exit(main_cli())
    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "--version"):
        sys.exit(main_cli())
    else:
        # Arrancar GUI por defecto (importando tkinter bajo demanda)
        try:
            from .gui.app import DLMusicApp
            app = DLMusicApp()
            app.mainloop()
        except Exception as e:
            print(f"Error iniciando GUI ({e}), cayendo a modo CLI...")
            sys.exit(main_cli())

if __name__ == "__main__":
    main()
