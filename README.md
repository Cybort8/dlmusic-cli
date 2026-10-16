# dlmusic-cli

Script de Bash para descargar canciones, playlists y álbumes en **la mejor calidad posible** desde **Spotify**, **YouTube** y **YouTube Music**, con solo pegar el enlace.

## Características

- **Detección automática** de la fuente según el enlace:
  - `open.spotify.com` → usa [`spotdl`](https://github.com/spotDL/spotify-downloader)
  - `music.youtube.com`, `youtube.com`, `youtu.be`, `youtube-nocookie.com`, `shorts.youtube.com`, `yt.be` → usa [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- **Máxima calidad**: sin re-codificaciones innecesarias (prioriza `m4a`/`opus`/`webm` originales con `--audio-quality 0`).
- **Metadatos completos**: título, artista, álbum, carátula y letras (cuando están disponibles).
- **Múltiples enlaces** en una sola ejecución.
- **Carpeta de salida configurable** con la variable `DLMUSIC_DIR`.

## Requisitos

| Herramienta | Para qué | Instalación (Arch) |
| --- | --- | --- |
| `bash` | Ejecutar el script | ya incluido |
| `ffmpeg` | Extraer/convertir audio y metadatos | `sudo pacman -S ffmpeg` |
| [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) | YouTube / YouTube Music | `sudo pacman -S yt-dlp` |
| [`spotdl`](https://github.com/spotDL/spotify-downloader) | Spotify | `python3 -m pip install --user --break-system-packages spotdl` |

> `spotdl` solo es necesario si vas a descargar desde Spotify.

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
./dlmusic.sh <URL> [<URL> ...]
```

### Ejemplos

```bash
# Una canción de Spotify
./dlmusic.sh "https://open.spotify.com/track/xxxxxxxx"

# Una playlist completa de Spotify
./dlmusic.sh "https://open.spotify.com/playlist/xxxxxxxx"

# Un video o playlist de YouTube Music
./dlmusic.sh "https://music.youtube.com/watch?v=xxxxxxxx"

# Varias fuentes a la vez
./dlmusic.sh "https://open.spotify.com/playlist/xxxx" "https://music.youtube.com/watch?v=yyyy"
```

## Configuración

| Variable | Descripción | Valor por defecto |
| --- | --- | --- |
| `DLMUSIC_DIR` | Carpeta donde se guardan las descargas | `~/Dev` |

```bash
DLMUSIC_DIR="$HOME/Music" ./dlmusic.sh "https://open.spotify.com/track/xxxx"
```

## Calidad de audio

El script prioriza **no recodificar** para no perder calidad:

- **YouTube / YouTube Music**: selecciona `bestaudio` priorizando `m4a` → `opus` → `webm` y usa `--audio-quality 0` (máxima disponible), añadiendo metadatos y miniatura.
- **Spotify**: usa `spotdl` con `--format m4a --bitrate auto`, incrustando metadatos, portada y letras.

Los archivos se guardan con el patrón:

```
<Artista> - <Título>.<ext>
```

## Requisitos legales

Descarga únicamente contenido que tengas derecho a descargar. Respeta los términos de servicio de Spotify y YouTube y las leyes de derechos de autor de tu país.

## Licencia

MIT
