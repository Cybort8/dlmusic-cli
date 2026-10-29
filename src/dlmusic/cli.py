import argparse
from pathlib import Path

from .config import load_config
from .core.detect import detect_platform
from .core.engines.spotify import SpotifyEngine
from .core.engines.youtube import YouTubeEngine


def main_cli(args=None):
    parser = argparse.ArgumentParser(description="dlmusic — Descarga música en la mejor calidad.")
    parser.add_argument("urls", nargs="*", help="URLs de Spotify, YouTube, SoundCloud, etc.")
    parser.add_argument("-o", "--output", help="Carpeta de salida")
    parser.add_argument("-f", "--format", default="m4a", help="Formato de audio (m4a, mp3, flac, opus)")
    parser.add_argument("-b", "--bitrate", default="auto", help="Bitrate (auto, 320k, etc.)")
    parser.add_argument("-j", "--jobs", type=int, default=4, help="Número de descargas paralelas")
    parser.add_argument("-e", "--engine", default="auto", help="Motor (auto, yt-dlp, spotdl)")
    parser.add_argument("--no-archive", action="store_true", help="Desactivar registro de duplicados")
    parser.add_argument("--cookies-browser", help="Navegador para extraer cookies (chrome, firefox, etc.)")
    parser.add_argument("--cookie-file", help="Archivo de cookies Netscape")
    parser.add_argument("--no-lyrics", action="store_true", help="No incrustar letras")
    parser.add_argument("--version", action="store_true", help="Mostrar versión")

    parsed = parser.parse_args(args)

    if parsed.version:
        print("dlmusic v2.1.0 (Python Core)")
        return 0

    if not parsed.urls:
        parser.print_help()
        return 1

    cfg = load_config()
    if parsed.output:
        cfg["music_dir"] = parsed.output
    if parsed.format:
        cfg["format"] = parsed.format
    if parsed.bitrate:
        cfg["bitrate"] = parsed.bitrate
    cfg["use_archive"] = not parsed.no_archive
    if parsed.cookies_browser:
        cfg["cookies_browser"] = parsed.cookies_browser
    if parsed.cookie_file:
        cfg["cookie_file"] = parsed.cookie_file
    cfg["lyrics"] = not parsed.no_lyrics

    cache_dir = cfg.get("cache_dir", str(Path.home() / ".cache" / "dlmusic"))
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    yt = YouTubeEngine()
    sp = SpotifyEngine()

    for url in parsed.urls:
        print(f"\n[dlmusic] Procesando: {url}")
        plat = detect_platform(url)
        engine = sp if plat == "spotify" else yt

        success = engine.download(
            url=url,
            output_dir=cfg["music_dir"],
            format_str=cfg["format"],
            bitrate=cfg["bitrate"],
            use_archive=cfg["use_archive"],
            archive_path=str(Path(cache_dir) / f"{plat}-archive.txt"),
            cookies_browser=cfg["cookies_browser"],
            cookie_file=cfg["cookie_file"],
            lyrics=cfg["lyrics"],
            callback=lambda ev: print(f"[{ev.status.upper()}] {ev.artist} - {ev.title} ({ev.percent:.1f}%) {ev.speed}")
        )
        if success:
            print(f"[✓] Descarga completada: {url}")
        else:
            print(f"[✗] Falló la descarga: {url}")

    return 0
