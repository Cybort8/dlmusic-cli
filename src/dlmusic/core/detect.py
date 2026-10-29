
def detect_platform(url: str) -> str:
    url_lower = url.strip().lower()
    if not url_lower:
        return "unknown"
    
    if "spotify.com" in url_lower or "open.spotify.com" in url_lower or url_lower.startswith("spotify:"):
        return "spotify"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower or "music.youtube.com" in url_lower:
        return "youtube"
    elif "soundcloud.com" in url_lower:
        return "soundcloud"
    elif "bandcamp.com" in url_lower:
        return "bandcamp"
    elif "apple.com" in url_lower and "music" in url_lower:
        return "applemusic"
    else:
        # Por defecto yt-dlp soporta cientos de sitios
        return "youtube"
