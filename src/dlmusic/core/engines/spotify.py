import os
import subprocess
import sys

from .base import BaseEngine, ProgressCallback, ProgressEvent


class SpotifyEngine(BaseEngine):
    def download(self, url: str, output_dir: str, format_str: str, bitrate: str, 
                 use_archive: bool, archive_path: str, cookies_browser: str, 
                 cookie_file: str, lyrics: bool, callback: ProgressCallback) -> bool:
        
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            sys.executable, "-m", "spotdl",
            url,
            "--output", os.path.join(output_dir, "{artist} - {title}.{output-ext}"),
            "--format", format_str
        ]

        if bitrate != "auto":
            cmd.extend(["--bitrate", bitrate])

        if use_archive and archive_path:
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            cmd.extend(["--archive", archive_path])

        if cookie_file and os.path.exists(cookie_file):
            cmd.extend(["--cookie-file", cookie_file])

        # spotdl ya incrusta letras por defecto o maneja syncedlyrics según versión
        callback(ProgressEvent(status='downloading', title=url, artist='Spotify'))

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if process.stdout:
                for line in process.stdout:
                    line_str = line.strip()
                    if not line_str:
                        continue
                    # Parsear output básico de spotdl
                    if "Downloading" in line_str or "Fetching" in line_str:
                        callback(ProgressEvent(status='downloading', title=line_str, artist='Spotify', percent=50.0))
                    elif "Converted" in line_str or "Saved" in line_str:
                        callback(ProgressEvent(status='finished', title=line_str, artist='Spotify', percent=100.0))

            process.wait()
            if process.returncode == 0:
                callback(ProgressEvent(status='finished', title='Completado', artist='Spotify', percent=100.0))
                return True
            else:
                callback(ProgressEvent(status='error', error_message=f"spotdl exit code {process.returncode}"))
                return False

        except Exception as e:
            callback(ProgressEvent(status='error', error_message=str(e)))
            return False
