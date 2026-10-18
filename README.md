# dlmusic-cli

Script de Bash para descargar canciones, playlists y álbumes en **la mejor calidad posible** desde **Spotify**, **YouTube**, **YouTube Music**, **SoundCloud**, **Bandcamp** y muchos sitios más, con solo pegar el enlace.

## Características

- **Detección automática** de la fuente según el enlace:
  - `open.spotify.com`, `spotify:...` → usa [`spotdl`](https://github.com/spotDL/spotify-downloader)
  - `youtube.com`, `music.youtube.com`, `youtu.be`, `soundcloud.com`, `bandcamp.com` y demás sitios soportados por [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) → usa `yt-dlp`
- **Máxima calidad**: prioriza el audio original y **evita recodificaciones** siempre que sea posible.
- **Menú interactivo**: ejecútalo sin argumentos y pega los enlaces.
- **Descargas en paralelo**: varias URLs a la vez, configurable con `-j`.
- **Metadatos completos**: título, artista, álbum, carátula y letras (cuando están disponibles).
- **Detección de duplicados**: no vuelve a descargar lo que ya bajaste.
- **Reintentos y manejo de errores**: reintenta fallos y continúa aunque una canción falle.
- **Formato y calidad configurables**: `mp3`, `m4a`, `opus`, `flac`, `ogg`, `wav` y bitrate.
- **Cookies**: soporte para playlists privadas / contenido con restricciones.
- **`--update`**: actualiza `yt-dlp` y `spotdl` al momento.

## Requisitos

| Herramienta | Para qué | Instalación (Arch) |
| --- | --- | --- |
| `bash` | Ejecutar el script | ya incluido |
| `ffmpeg` | Extraer/convertir audio y metadatos | `sudo pacman -S ffmpeg` |
| [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) | YouTube, SoundCloud, Bandcamp y más | `sudo pacman -S yt-dlp` |
| [`spotdl`](https://github.com/spotDL/spotify-downloader) | Spotify | `python3 -m pip install --user --break-system-packages spotdl` |

> `spotdl` solo es necesario si descargas desde Spotify.

## Instalación

```bash
git clone https://github.com/Cybort8/dlmusic-cli.git
cd dlmusic-cli
chmod +x dlmusic.sh
```

Opcional: añádelo al `PATH` para ejecutarlo desde cualquier lado.

```bash
mkdir -p ~/.local/bin
ln -sf "$PWD/dlmusic.sh" ~/.local/bin/dlmusic
```

## Uso

```bash
./dlmusic.sh [opciones] <URL> [<URL> ...]
./dlmusic.sh            # menú interactivo
```

### Ejemplos

```bash
# Una canción de Spotify
./dlmusic.sh "https://open.spotify.com/track/xxxxxxxx"

# Una playlist completa de Spotify
./dlmusic.sh "https://open.spotify.com/playlist/xxxxxxxx"

# YouTube Music o YouTube
./dlmusic.sh "https://music.youtube.com/watch?v=xxxxxxxx"

# Varias fuentes a la vez
./dlmusic.sh "https://open.spotify.com/playlist/xxxx" "https://soundcloud.com/xxxx"

# Elegir formato y carpeta
./dlmusic.sh -f mp3 -o "$HOME/Música" "https://open.spotify.com/track/xxxx"

# Con cookies del navegador (contenido con restricciones)
./dlmusic.sh --cookies-from-browser firefox "https://www.youtube.com/playlist?list=xxxx"
```

## Opciones

| Opción | Descripción | Por defecto |
| --- | --- | --- |
| `-i, --interactive` | Abrir el menú interactivo | — |
| `-o, --output DIR` | Carpeta de salida | `$HOME/Music` |
| `-f, --format FMT` | Formato: `mp3\|m4a\|opus\|flac\|ogg\|wav` | `m4a` |
| `-b, --bitrate BR` | Bitrate | `auto` |
| `-j, --jobs N` | URLs en paralelo | nº de CPUs |
| `-t, --threads N` | Hilos por descarga / fragmentos | `4` |
| `-e, --engine ENGINE` | `auto\|spotdl\|ytdlp` | `auto` |
| `-r, --retries N` | Reintentos por descarga | `5` |
| `--no-lyrics` | No descargar letras (solo Spotify) | — |
| `-n, --no-archive` | No omitir canciones ya descargadas | — |
| `--cookies-from-browser B` | Usar cookies del navegador (firefox, chrome…) | — |
| `--cookies FILE` | Archivo de cookies (formato Netscape) | — |
| `-u, --update` | Actualizar yt-dlp y spotdl | — |
| `-h, --help` | Ayuda | — |
| `-v, --version` | Versión | — |

### Variables de entorno

`DLMUSIC_DIR`, `DLMUSIC_FORMAT`, `DLMUSIC_BITRATE`, `DLMUSIC_JOBS`, `DLMUSIC_THREADS`, `DLMUSIC_ENGINE`, `DLMUSIC_RETRIES`, `DLMUSIC_LYRICS`, `DLMUSIC_COOKIES_BROWSER`, `DLMUSIC_COOKIE_FILE`.

```bash
DLMUSIC_FORMAT=opus DLMUSIC_DIR="$HOME/Música" ./dlmusic.sh "https://open.spotify.com/track/xxxx"
```

## Calidad de audio

El script prioriza **no recodificar** para no perder calidad:

- **YouTube / YouTube Music / SoundCloud / Bandcamp**: selecciona el mejor audio (`m4a` → `opus` → …) y con `--audio-quality 0` usa la máxima calidad disponible, incrustando metadatos y carátula.
- **Spotify**: usa `spotdl` con `--bitrate auto`, incrustando metadatos, portada y letras. El audio proviene del mejor match disponible (YouTube Music, etc.).

Los archivos se guardan con el patrón:

```
<Artista> - <Título>.<ext>
```

## Detección de duplicados

Se guardan archivos de archivo (*archive*) por motor en `~/.cache/dlmusic/` para no volver a descargar lo mismo. Para forzar una descarga usa `-n` o borra esos archivos.

## Requisitos legales

Descarga únicamente contenido que tengas derecho a descargar. Respeta los términos de servicio de Spotify y YouTube y las leyes de derechos de autor de tu país.

## Licencia

MIT
