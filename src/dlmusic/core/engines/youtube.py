import os

import yt_dlp

from ...platforms import find_binary
from .base import BaseEngine, ProgressCallback, ProgressEvent


class YouTubeEngine(BaseEngine):
    def download(self, url: str, output_dir: str, format_str: str, bitrate: str, 
                 use_archive: bool, archive_path: str, cookies_browser: str, 
                 cookie_file: str, lyrics: bool, callback: ProgressCallback) -> bool:
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Mapeo de formatos para max quality sin re-encode innecesario
        # Si pide m4a, prefer m4a/bestaudio; si flac, flac; si mp3, mp3
        ext = format_str.lower()
        if ext == "m4a":
            preferred_format = "bestaudio[ext=m4a]/bestaudio"
        elif ext == "flac":
            preferred_format = "bestaudio[ext=flac]/bestaudio"
        elif ext == "opus":
            preferred_format = "bestaudio[ext=opus]/bestaudio"
        else:
            preferred_format = "bestaudio/best"

        outtmpl = os.path.join(output_dir, "%(artist,uploader|Unknown Artist)s - %(title)s.%(ext)s")
        
        ydl_opts = {
            'format': preferred_format,
            'outtmpl': outtmpl,
            'noplaylist': False,
            'extract_flat': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ext,
                'preferredquality': '0' if bitrate == 'auto' else bitrate,
            }],
            'quiet': True,
            'no_warnings': True,
        }

        ffmpeg_path = find_binary("ffmpeg")
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        deno_path = find_binary("deno")
        if deno_path:
            ydl_opts['js_runtimes'] = ['deno']

        if use_archive and archive_path:
            os.makedirs(os.path.dirname(archive_path), exist_ok=True)
            ydl_opts['download_archive'] = archive_path

        if cookies_browser:
            ydl_opts['cookiesfrombrowser'] = (cookies_browser,)
        elif cookie_file and os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file

        def hook(d):
            status = d.get('status')
            title = d.get('info_dict', {}).get('title', 'Unknown')
            artist = d.get('info_dict', {}).get('artist', d.get('info_dict', {}).get('uploader', 'Unknown Artist'))
            
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                pct = (downloaded / total * 100) if total > 0 else 0.0
                speed = d.get('_speed_str', '0 B/s')
                eta = d.get('_eta_str', 'Unknown')
                callback(ProgressEvent(
                    status='downloading',
                    title=title,
                    artist=artist,
                    percent=pct,
                    downloaded_bytes=downloaded,
                    total_bytes=total if total > 0 else None,
                    speed=speed,
                    eta=eta
                ))
            elif status == 'finished':
                filepath = d.get('filename', '')
                callback(ProgressEvent(
                    status='finished',
                    title=title,
                    artist=artist,
                    percent=100.0,
                    filepath=filepath
                ))

        ydl_opts['progress_hooks'] = [hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            callback(ProgressEvent(
                status='error',
                error_message=str(e)
            ))
            return False
