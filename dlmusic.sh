#!/usr/bin/env bash
set -euo pipefail

MUSIC_DIR="${DLMUSIC_DIR:-$HOME/Dev}"
mkdir -p "$MUSIC_DIR"

usage() {
  cat <<'EOF'
Uso: ./dlmusic.sh <URL> [<URL> ...]

Descarga canciones/playlists en máxima calidad desde:
- Spotify (open.spotify.com)  -> usa spotdl
- YouTube/YouTube Music      -> usa yt-dlp

Variables:
  DLMUSIC_DIR  Carpeta de salida (por defecto: ~/Dev)

Ejemplos:
  ./dlmusic.sh "https://open.spotify.com/track/..."
  ./dlmusic.sh "https://open.spotify.com/playlist/..." "https://music.youtube.com/watch?v=..."
EOF
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

command -v yt-dlp >/dev/null || { echo "Falta yt-dlp"; exit 1; }
command -v ffmpeg >/dev/null || { echo "Falta ffmpeg"; exit 1; }

has_spotdl() { command -v spotdl >/dev/null 2>&1; }

download_yt() {
  local url="$1"
  echo "→ [yt-dlp] $url"
  yt-dlp \
    -f "bestaudio[ext=m4a]/bestaudio[ext=opus]/bestaudio[ext=webm]/bestaudio" \
    --extract-audio \
    --audio-quality 0 \
    --add-metadata \
    --embed-thumbnail \
    --parse-metadata "%(title)s:%(meta_title)s" \
    --parse-metadata "%(uploader)s:%(meta_artist)s" \
    -o "$MUSIC_DIR/%(artist)s - %(title)s.%(ext)s" \
    "$url"
}

download_spotify() {
  local url="$1"
  if ! has_spotdl; then
    echo "Error: spotdl no está instalado."
    echo "Instálalo con: python3 -m pip install --user --break-system-packages spotdl"
    exit 2
  fi
  echo "→ [spotdl] $url"
  spotdl download "$url" \
    --output "$MUSIC_DIR/{artist} - {title}.{ext}" \
    --format m4a \
    --bitrate auto \
    --embed-metadata \
    --embed-cover \
    --lyrics auto \
    --log-level INFO
}

for url in "$@"; do
  case "$url" in
    *open.spotify.com*) download_spotify "$url" ;;
    *music.youtube.com*|*youtube.com*|*youtu.be*|*youtube-nocookie.com*|*shorts.youtube.com*|*yt.be*) download_yt "$url" ;;
    *)
      echo "URL no reconocida: $url"
      echo "Usa enlaces de Spotify, YouTube o YouTube Music."
      exit 3
      ;;
  esac
done

echo "✓ Descargas completadas en: $MUSIC_DIR"
