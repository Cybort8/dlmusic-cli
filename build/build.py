from PyInstaller.__main__ import run

def build():
    print("[dlmusic] Generando ejecutable autocontenido con PyInstaller...")
    run(["build/dlmusic.spec", "--noconfirm"])
    print("[dlmusic] ¡Build completada en dist/dlmusic!")

if __name__ == "__main__":
    build()
