import sys

from dlmusic.cli import main_cli
from dlmusic.gui.app import DLMusicApp


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        sys.argv.pop(1)
        sys.exit(main_cli())
    elif len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "--version"):
        sys.exit(main_cli())
    else:
        try:
            app = DLMusicApp()
            app.mainloop()
        except Exception as e:
            print(f"Error iniciando GUI ({e}), cayendo a modo CLI...")
            sys.exit(main_cli())

if __name__ == "__main__":
    main()
