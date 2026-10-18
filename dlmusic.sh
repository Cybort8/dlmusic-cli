#!/usr/bin/env bash
#
# dlmusic — descarga canciones/playlists en la mejor calidad posible
# desde Spotify, YouTube, YouTube Music, SoundCloud, Bandcamp y más.
#
set -uo pipefail

PROG="$(basename "$0")"
VERSION="2.0.0"

# ---------------------------------------------------------------- defaults ---
MUSIC_DIR="${DLMUSIC_DIR:-$HOME/Music}"
FORMAT="${DLMUSIC_FORMAT:-m4a}"
BITRATE="${DLMUSIC_BITRATE:-auto}"
JOBS="${DLMUSIC_JOBS:-$(nproc 2>/dev/null || echo 4)}"
THREADS="${DLMUSIC_THREADS:-4}"
ENGINE="${DLMUSIC_ENGINE:-auto}"
RETRIES="${DLMUSIC_RETRIES:-5}"
LYRICS="${DLMUSIC_LYRICS:-yes}"
COOKIES_BROWSER="${DLMUSIC_COOKIES_BROWSER:-}"
COOKIE_FILE="${DLMUSIC_COOKIE_FILE:-}"
USE_ARCHIVE=yes
INTERACTIVE=0

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/dlmusic"
YTDLP_ARCHIVE="$CACHE_DIR/ytdlp-archive.txt"
SPOTDL_ARCHIVE="$CACHE_DIR/spotdl-archive.txt"
LOG_DIR="$CACHE_DIR/logs"

urls=()

# ------------------------------------------------------------------- color ---
if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'; C_CYAN=$'\033[36m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_CYAN=""
fi

log()  { printf '%s\n' "$*"; }
info() { printf '%s%s%s\n' "$C_CYAN" "$*" "$C_RESET"; }
ok()   { printf '%s%s%s\n' "$C_GREEN" "$*" "$C_RESET"; }
warn() { printf '%s%s%s\n' "$C_YELLOW" "$*" "$C_RESET" >&2; }
die()  { printf '%s%s%s\n' "$C_RED" "$*" "$C_RESET" >&2; exit 1; }

# ------------------------------------------------------------------- usage ---
usage() {
  cat <<EOF
${C_BOLD}$PROG $VERSION${C_RESET} — descarga música en la mejor calidad posible.

${C_BOLD}USO${C_RESET}
  $PROG [opciones] <URL> [<URL> ...]
  $PROG                       # menú interactivo

${C_BOLD}FUENTES SOPORTADAS${C_RESET}
  Spotify (open.spotify.com, spotify:...)      -> spotdl
  YouTube / YouTube Music (youtube.com, youtu.be, music.youtube.com)
  SoundCloud, Bandcamp y muchos más            -> yt-dlp

${C_BOLD}OPCIONES${C_RESET}
  -i, --interactive          Abrir el menú interactivo
  -o, --output DIR           Carpeta de salida (def: \$HOME/Music)
  -f, --format FMT           Formato: mp3|m4a|opus|flac|ogg|wav (def: m4a)
  -b, --bitrate BR           Bitrate (def: auto)
  -j, --jobs N               URLs en paralelo (def: nº de CPUs)
  -t, --threads N            Hilos por descarga / fragmentos (def: 4)
  -e, --engine ENGINE        auto|spotdl|ytdlp (def: auto)
  -r, --retries N            Reintentos por descarga (def: 5)
      --no-lyrics            No descargar letras (solo Spotify)
  -n, --no-archive           No omitir canciones ya descargadas
      --cookies-from-browser BROWSER   Usar cookies de navegador (firefox, chrome...)
      --cookies FILE         Archivo de cookies (formato Netscape)
  -u, --update               Actualizar yt-dlp y spotdl
  -h, --help                 Mostrar esta ayuda
  -v, --version              Mostrar la versión

${C_BOLD}VARIABLES DE ENTORNO${C_RESET}
  DLMUSIC_DIR, DLMUSIC_FORMAT, DLMUSIC_BITRATE, DLMUSIC_JOBS,
  DLMUSIC_THREADS, DLMUSIC_ENGINE, DLMUSIC_RETRIES, DLMUSIC_LYRICS,
  DLMUSIC_COOKIES_BROWSER, DLMUSIC_COOKIE_FILE

${C_BOLD}EJEMPLOS${C_RESET}
  $PROG "https://open.spotify.com/playlist/xxxx"
  $PROG "https://music.youtube.com/watch?v=xxxx" "https://soundcloud.com/..."
  $PROG -f mp3 -o "\$HOME/Música" "https://open.spotify.com/track/xxxx"
EOF
}

# --------------------------------------------------------------- validate ----
valid_format() {
  case "$1" in
    mp3|m4a|opus|flac|ogg|wav) return 0 ;;
    *) return 1 ;;
  esac
}

require_tools() {
  [[ -n "${MUSIC_DIR:-}" ]] || die "Carpeta de salida vacía."
  command -v ffmpeg >/dev/null || die "Falta 'ffmpeg'. Instálalo: sudo pacman -S ffmpeg"
  command -v yt-dlp >/dev/null || warn "yt-dlp no encontrado: las fuentes de YouTube/SoundCloud/etc. fallarán."
}

# ----------------------------------------------------------------- yt-dlp ----
ytdlp_format_selector() {
  case "$FORMAT" in
    m4a)  printf '%s' "bestaudio[ext=m4a]/bestaudio[ext=opus]/bestaudio/best" ;;
    opus) printf '%s' "bestaudio[ext=opus]/bestaudio[ext=webm]/bestaudio/best" ;;
    *)    printf '%s' "bestaudio/best" ;;
  esac
}

download_ytdlp() {
  local url="$1"
  local -a args=(
    -f "$(ytdlp_format_selector)"
    -x --audio-format "$FORMAT" --audio-quality "$BITRATE"
    --add-metadata --embed-thumbnail
    --parse-metadata "%(artist,uploader|Unknown Artist)s:%(meta_artist)s"
    --parse-metadata "%(title)s:%(meta_title)s"
    --retries "$RETRIES" --fragment-retries "$RETRIES"
    -N "$THREADS"
    -i --no-overwrites --newline
    -o "$MUSIC_DIR/%(artist,uploader|Unknown Artist)s - %(title)s.%(ext)s"
  )
  [[ "$USE_ARCHIVE" == yes ]] && args+=( --download-archive "$YTDLP_ARCHIVE" )
  [[ -n "$COOKIE_FILE" ]]    && args+=( --cookies "$COOKIE_FILE" )
  [[ -n "$COOKIES_BROWSER" ]] && args+=( --cookies-from-browser "$COOKIES_BROWSER" )

  yt-dlp "${args[@]}" "$url"
}

# ----------------------------------------------------------------- spotdl ----
download_spotdl() {
  local url="$1"
  command -v spotdl >/dev/null || {
    die "Spotify requiere 'spotdl'. Instálalo:
  python3 -m pip install --user --break-system-packages spotdl"
  }
  local -a args=(
    download "$url"
    --output "$MUSIC_DIR/{artist} - {title}.{output-ext}"
    --format "$FORMAT"
    --bitrate "$BITRATE"
    --threads "$THREADS"
    --max-retries "$RETRIES"
    --print-errors
    --log-level INFO
  )
  [[ "$USE_ARCHIVE" == yes ]] && args+=( --archive "$SPOTDL_ARCHIVE" )
  [[ "$LYRICS" == yes ]]     && args+=( --lyrics genius musixmatch )
  [[ -n "$COOKIE_FILE" ]]    && args+=( --cookie-file "$COOKIE_FILE" )
  [[ -n "$COOKIES_BROWSER" ]] && warn "spotdl no admite --cookies-from-browser; usa --cookies FILE."

  spotdl "${args[@]}"
}

# ------------------------------------------------------------- dispatcher ----
detect_engine_for() {
  local url="$1"
  if [[ "$ENGINE" != "auto" ]]; then printf '%s' "$ENGINE"; return; fi
  case "$url" in
    *open.spotify.com*|*spotify.com*|spotify:*|"album:"*|"playlist:"*|"artist:"*|"track:"*) printf 'spotdl' ;;
    *) printf 'ytdlp' ;;
  esac
}

download_url() {
  local url="$1"
  local engine
  engine="$(detect_engine_for "$url")"
  case "$engine" in
    spotdl) download_spotdl "$url" ;;
    ytdlp)  download_ytdlp "$url" ;;
    *)      die "Motor desconocido: $engine" ;;
  esac
}

# ----------------------------------------------------------------- update ----
do_update() {
  local rc=0
  if command -v yt-dlp >/dev/null; then
    info "==> Actualizando yt-dlp"
    yt-dlp -U 2>&1 | sed 's/^/    /' || rc=1
  fi
  if command -v spotdl >/dev/null; then
    info "==> Actualizando spotdl"
    python3 -m pip install --user --break-system-packages --upgrade spotdl 2>&1 | tail -n 3 | sed 's/^/    /' || rc=1
  fi
  [[ $rc -eq 0 ]] && ok "Actualización completada." || warn "Alguna herramienta no pudo actualizarse (¿instalada por el sistema?)."
  return $rc
}

# -------------------------------------------------------------- interactive --
interactive_menu() {
  printf '%s\n' "${C_BOLD}═══════════ dlmusic $VERSION — modo interactivo ═══════════${C_RESET}"
  echo
  printf 'Carpeta de salida [%s]: ' "$MUSIC_DIR"
  read -r answer
  [[ -n "$answer" ]] && MUSIC_DIR="$answer"

  printf 'Formato [mp3|m4a|opus|flac|ogg|wav] (%s): ' "$FORMAT"
  read -r answer
  if [[ -n "$answer" ]]; then
    valid_format "$answer" || die "Formato inválido: $answer"
    FORMAT="$answer"
  fi

  printf 'Descargas en paralelo (%s): ' "$JOBS"
  read -r answer
  [[ -n "$answer" ]] && JOBS="$answer"

  [[ "$USE_ARCHIVE" == yes ]] && printf '%sOmitir canciones ya descargadas: SÍ%s\n' "$C_DIM" "$C_RESET"

  echo
  info "Pega los enlaces (uno por línea). Deja una línea vacía para terminar:"
  local line
  while IFS= read -r line; do
    [[ -z "$line" ]] && break
    urls+=("$line")
  done

  (( ${#urls[@]} )) || die "No introdujiste ningún enlace."
  echo
  log "${C_BOLD}Se descargarán ${#urls[@]} enlace(s) en $MUSIC_DIR ($FORMAT):${C_RESET}"
  local u
  for u in "${urls[@]}"; do log "  • $u"; done
  printf '¿Continuar? [S/n]: '
  read -r answer
  case "$answer" in n|N|no|NO) die "Cancelado." ;; esac
}

# ------------------------------------------------------------------ runner ---
run_all() {
  local total=${#urls[@]}
  local ok_count=0 fail_count=0
  local -a failed_urls=()
  local -a pids=()
  local -a job_urls=()

  mkdir -p "$MUSIC_DIR" "$CACHE_DIR" "$LOG_DIR" || die "No se pudo crear $MUSIC_DIR"

  if (( JOBS <= 1 )) || (( total == 1 )); then
    # Secuencial: progreso en vivo
    local url
    for url in "${urls[@]}"; do
      info "→ Descargando: $url"
      if download_url "$url"; then
        ok "✓ Completado: $url"; ok_count=$((ok_count + 1))
      else
        warn "✗ Falló: $url"; fail_count=$((fail_count + 1)); failed_urls+=("$url")
      fi
    done
  else
    # Paralelo
    local i=0
    local url
    for url in "${urls[@]}"; do
      while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n 2>/dev/null || true; done
      local logfile="$LOG_DIR/job_$i.log"
      ( download_url "$url" >"$logfile" 2>&1 ) &
      pids+=($!)
      job_urls+=("$url")
      info "→ En cola ($((i + 1))/$total): $url"
      i=$((i + 1))
    done

    local idx=0
    local pid
    for pid in "${pids[@]}"; do
      if wait "$pid"; then
        ok "✓ Completado: ${job_urls[$idx]}"; ok_count=$((ok_count + 1))
      else
        warn "✗ Falló: ${job_urls[$idx]}"
        fail_count=$((fail_count + 1)); failed_urls+=("${job_urls[$idx]}")
        tail -n 12 "$LOG_DIR/job_$idx.log" 2>/dev/null | sed 's/^/    /' >&2
      fi
      idx=$((idx + 1))
    done
  fi

  echo
  log "${C_BOLD}═══════════════ Resumen ═══════════════${C_RESET}"
  ok "  Completadas: $ok_count"
  (( fail_count )) && warn "  Fallidas:    $fail_count"
  log "  Carpeta:     $MUSIC_DIR"
}

# ------------------------------------------------------------------ parse ----
parse_args() {
  while (( $# )); do
    case "$1" in
      -h|--help)    usage; exit 0 ;;
      -v|--version) echo "$PROG $VERSION"; exit 0 ;;
      -u|--update)  do_update; exit $? ;;
      -i|--interactive) INTERACTIVE=1; shift ;;
      -o|--output)  [[ $# -ge 2 ]] || die "Falta el valor de $1"; MUSIC_DIR="$2"; shift 2 ;;
      -f|--format)  [[ $# -ge 2 ]] || die "Falta el valor de $1"; FORMAT="$2"; shift 2 ;;
      -b|--bitrate) [[ $# -ge 2 ]] || die "Falta el valor de $1"; BITRATE="$2"; shift 2 ;;
      -j|--jobs)    [[ $# -ge 2 ]] || die "Falta el valor de $1"; JOBS="$2"; shift 2 ;;
      -t|--threads) [[ $# -ge 2 ]] || die "Falta el valor de $1"; THREADS="$2"; shift 2 ;;
      -e|--engine)  [[ $# -ge 2 ]] || die "Falta el valor de $1"; ENGINE="$2"; shift 2 ;;
      -r|--retries) [[ $# -ge 2 ]] || die "Falta el valor de $1"; RETRIES="$2"; shift 2 ;;
      -n|--no-archive) USE_ARCHIVE=no; shift ;;
      --no-lyrics)  LYRICS=no; shift ;;
      --cookies-from-browser) [[ $# -ge 2 ]] || die "Falta el valor de $1"; COOKIES_BROWSER="$2"; shift 2 ;;
      --cookies)    [[ $# -ge 2 ]] || die "Falta el valor de $1"; COOKIE_FILE="$2"; shift 2 ;;
      --)           shift; while (( $# )); do urls+=("$1"); shift; done ;;
      -*)           die "Opción desconocida: $1 (usa --help)" ;;
      *)            urls+=("$1"); shift ;;
    esac
  done
}

# -------------------------------------------------------------------- main ---
main() {
  parse_args "$@"

  valid_format "$FORMAT" || die "Formato inválido: $FORMAT (usa mp3|m4a|opus|flac|ogg|wav)"
  case "$ENGINE" in auto|spotdl|ytdlp) ;; *) die "Motor inválido: $ENGINE (usa auto|spotdl|ytdlp)" ;; esac
  [[ "$JOBS" =~ ^[0-9]+$ ]] && (( JOBS > 0 )) || die "Jobs inválido: $JOBS"
  [[ "$THREADS" =~ ^[0-9]+$ ]] && (( THREADS > 0 )) || die "Threads inválido: $THREADS"

  if (( ${#urls[@]} == 0 )); then
    INTERACTIVE=1
  fi
  (( INTERACTIVE )) && interactive_menu

  require_tools

  echo
  log "${C_BOLD}dlmusic $VERSION${C_RESET} — ${#urls[@]} enlace(s) → $MUSIC_DIR (formato: $FORMAT, jobs: $JOBS)"
  echo

  run_all
}

main "$@"
