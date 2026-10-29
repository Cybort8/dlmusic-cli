from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ProgressEvent:
    status: str          # downloading, finished, error, info
    title: str = ""
    artist: str = ""
    percent: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int | None = None
    speed: str = ""
    eta: str = ""
    error_message: str = ""
    filepath: str = ""

ProgressCallback = Callable[[ProgressEvent], None]

class BaseEngine:
    def download(self, url: str, output_dir: str, format_str: str, bitrate: str, 
                 use_archive: bool, archive_path: str, cookies_browser: str, 
                 cookie_file: str, lyrics: bool, callback: ProgressCallback) -> bool:
        raise NotImplementedError
