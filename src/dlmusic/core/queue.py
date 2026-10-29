from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from .detect import detect_platform
from .engines.base import ProgressEvent
from .engines.spotify import SpotifyEngine
from .engines.youtube import YouTubeEngine


class DownloadManager:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.yt_engine = YouTubeEngine()
        self.spotify_engine = SpotifyEngine()
        self._cancelled = False

    def cancel_all(self):
        self._cancelled = True

    def download_url(self, url: str, cfg: dict, callback: Callable[[str, ProgressEvent], None]) -> bool:
        if self._cancelled:
            return False

        platform = detect_platform(url)
        engine = self.spotify_engine if platform == "spotify" else self.yt_engine

        cache_dir = cfg.get("cache_dir", "")
        use_archive = cfg.get("use_archive", True)
        archive_path = f"{cache_dir}/{platform}-archive.txt" if cache_dir else ""

        def internal_callback(ev: ProgressEvent):
            callback(url, ev)

        success = engine.download(
            url=url,
            output_dir=cfg.get("music_dir", ""),
            format_str=cfg.get("format", "m4a"),
            bitrate=cfg.get("bitrate", "auto"),
            use_archive=use_archive,
            archive_path=archive_path,
            cookies_browser=cfg.get("cookies_browser", ""),
            cookie_file=cfg.get("cookie_file", ""),
            lyrics=cfg.get("lyrics", True),
            callback=internal_callback
        )
        return success
