import sys
from pathlib import Path


def get_bundled_dir() -> Path:
    """Retorna la ruta base de los binarios empaquetados o del entorno."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent

def find_binary(name: str) -> str:
    """Busca un binario (ffmpeg, deno) embebido o en el PATH del sistema."""
    bundled = get_bundled_dir() / "assets" / name
    if bundled.exists():
        return str(bundled)
    
    # Comprobar si existe extensión .exe en Windows
    if sys.platform == "win32":
        bundled_exe = get_bundled_dir() / "assets" / f"{name}.exe"
        if bundled_exe.exists():
            return str(bundled_exe)
            
    # Buscar en PATH
    import shutil
    sys_bin = shutil.which(name)
    if sys_bin:
        return sys_bin
        
    return name
