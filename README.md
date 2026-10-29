# dlmusic

Descarga canciones, playlists y álbumes en **la mejor calidad posible** desde **Spotify**, **YouTube**, **YouTube Music**, **SoundCloud**, **Bandcamp** y muchos sitios más, con solo pegar el enlace.

Versión actual: **2.1.0** (Python, interfaz gráfica + CLI).

## Características

- **Detección automática** de la fuente según el enlace:
  - `open.spotify.com`, `spotify:...` → usa [`spotdl`](https://github.com/spotDL/spotify-downloader)
  - `youtube.com`, `music.youtube.com`, `youtu.be`, `soundcloud.com`, `bandcamp.com` y demás sitios soportados por [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) → usa `yt-dlp`
- **Interfaz gráfica** (CustomTkinter) con cola de descargas, progreso por elemento, ajustes y registros.
- **Modo CLI** con paridad de flags para scripts y terminal.
- **Máxima calidad**: prioriza el audio original y **evita recodificaciones** siempre que sea posible.
- **Descargas en paralelo**: varias URLs a la vez, configurable con `-j`.
- **Metadatos completos**: título, artista, álbum, carátula y letras (cuando están disponibles).
- **Detección de duplicados**: no vuelve a descargar lo que ya bajaste.
- **Reintentos y manejo de errores**: reintenta fallos y continúa aunque una canción falle.
- **Formato y calidad configurables**: `mp3`, `m4a`, `opus`, `flac`, `ogg`, `wav` y bitrate.
- **Cookies**: soporte para playlists privadas / contenido con restricciones.
- **Idiomas**: español e inglés, seleccionable desde la GUI.
- **Multiplataforma**: Linux, macOS y Windows.

## Requisitos

### Para usar la app empaquetada (recomendado)
Nada. Descarga el artefacto de la [página de releases](https://github.com/Cybort8/dlmusic-cli/releases) y ejecútalo:
- **Linux**: `dlmusic` (AppImage) — `chmod +x dlmusic && ./dlmusic`
- **macOS**: `dlmusic.dmg` → arrastra `dlmusic.app` a Aplicaciones. (Sin firma: si Gatekeeper bloquea, ejecuta `xattr -dr com.apple.quarantine /Applications/dlmusic.app`)
- **Windows**: `dlmusic.zip` → extrae y ejecuta `dlmusic.exe`. (SmartScreen puede avisar; elige "Más información → Ejecutar de todas formas")

### Para desarrollar / ejecutar desde código fuente
| Herramienta | Para qué | Instalación (Arch) |
| --- | --- | --- |
| Python ≥ 3.10 | Ejecutar el proyecto | `sudo pacman -S python` |
| `tk` | Interfaz gráfica | `sudo pacman -S tk` |
| `ffmpeg` | Extraer/convertir audio y metadatos | `sudo pacman -S ffmpeg` |
| [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) | YouTube, SoundCloud, Bandcamp y más | `sudo pacman -S yt-dlp` |
| [`spotdl`](https://github.com/spotDL/spotify-downloader) | Spotify | `python3 -m pip install --user --break-system-packages spotdl` |
| Deno / Node | Runtime JS para YouTube (yt-dlp) | `sudo pacman -S deno` |

> `spotdl` solo es necesario si descargas desde Spotify. `yt-dlp` se instala como dependencia Python automáticamente.

## Instalación (desde código fuente)

```bash
git clone https://github.com/Cybort8/dlmusic-cli.git
cd dlmusic-cli
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e .[dev]
```

## Uso

### Interfaz gráfica (por defecto)

```bash
python -m dlmusic
# o, tras instalar:
dlmusic
```

Pega las URLs (una por línea) en la caja superior, elige formato/carpeta en **Ajustes** y pulsa **Iniciar Descargas**. La cola muestra progreso, velocidad y ETA por elemento; puedes cancelar o reintentar.

### Modo CLI

```bash
python -m dlmusic --cli [opciones] <URL> [<URL> ...]
# o:
dlmusic --cli [opciones] <URL> [<URL> ...]
```

#### Ejemplos

```bash
# Una canción de Spotify
python -m dlmusic --cli "https://open.spotify.com/track/xxxxxxxx"

# Una playlist completa de Spotify
python -m dlmusic --cli "https://open.spotify.com/playlist/xxxxxxxx"

# YouTube Music o YouTube
python -m dlmusic --cli "https://music.youtube.com/watch?v=xxxxxxxx"

# Varias fuentes a la vez
python -m dlmusic --cli "https://open.spotify.com/playlist/xxxx" "https://soundcloud.com/xxxx"

# Elegir formato y carpeta
python -m dlmusic --cli -f mp3 -o "$HOME/Música" "https://open.spotify.com/track/xxxx"

# Con cookies del navegador (contenido con restricciones)
python -m dlmusic --cli --cookies-browser firefox "https://www.youtube.com/playlist?list=xxxx"
```

### Menú interactivo (wrapper legacy)

```bash
./dlmusic.sh
```

## Opciones (CLI)

| Opción | Descripción | Por defecto |
| --- | --- | --- |
| `-o, --output DIR` | Carpeta de salida | `~/Music/Dilan` |
| `-f, --format FMT` | Formato: `mp3\|m4a\|opus\|flac\|ogg\|wav` | `m4a` |
| `-b, --bitrate BR` | Bitrate | `auto` |
| `-j, --jobs N` | URLs en paralelo | `4` |
| `-e, --engine ENGINE` | `auto\|spotdl\|ytdlp` | `auto` |
| `--no-archive` | No omitir canciones ya descargadas | — |
| `--cookies-browser B` | Usar cookies del navegador (firefox, chrome…) | — |
| `--cookie-file FILE` | Archivo de cookies (formato Netscape) | — |
| `--no-lyrics` | No descargar letras (solo Spotify) | — |
| `-h, --help` | Ayuda | — |
| `-v, --version` | Versión | — |

### Variables de entorno

`DLMUSIC_DIR`, `DLMUSIC_FORMAT`, `DLMUSIC_BITRATE`, `DLMUSIC_JOBS`, `DLMUSIC_THREADS`, `DLMUSIC_ENGINE`, `DLMUSIC_RETRIES`, `DLMUSIC_LYRICS`, `DLMUSIC_COOKIES_BROWSER`, `DLMUSIC_COOKIE_FILE`.

```bash
DLMUSIC_FORMAT=opus DLMUSIC_DIR="$HOME/Música" python -m dlmusic --cli "https://open.spotify.com/track/xxxx"
```

## Calidad de audio

El programa prioriza **no recodificar** para no perder calidad:

- **YouTube / YouTube Music / SoundCloud / Bandcamp**: selecciona el mejor audio (`m4a` → `opus` → …) y con `--audio-quality 0` usa la máxima calidad disponible, incrustando metadatos y carátula.
- **Spotify**: usa `spotdl` con `--bitrate auto`, incrustando metadatos, portada y letras. El audio proviene del mejor match disponible (YouTube Music, etc.).

Los archivos se guardan con el patrón:

```
<Artista> - <Título>.<ext>
```

## Detección de duplicados

Se guardan archivos de archivo (*archive*) por motor en el directorio de caché del usuario (`platformdirs`) para no volver a descargar lo mismo. Para forzar una descarga usa `--no-archive` o borra esos archivos.

## Empaquetado (desarrolladores)

```bash
python build/build.py          # genera dist/dlmusic/ (onedir)
```

Para incluir binarios externos, colócalos en `assets/` antes de compilar (`ffmpeg`, `ffprobe`, `deno`). Las releases multi-OS se generan con `.github/workflows/release.yml` al crear un tag `v*`.

## Requisitos legales

Descarga únicamente contenido que tengas derecho a descargar. Respeta los términos de servicio de Spotify y YouTube y las leyes de derechos de autor de tu país.

## Licencia

MIT