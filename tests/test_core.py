from dlmusic.config import load_config
from dlmusic.core.detect import detect_platform


def test_detect_platform():
    assert detect_platform("https://open.spotify.com/track/123") == "spotify"
    assert detect_platform("https://youtube.com/watch?v=123") == "youtube"
    assert detect_platform("https://youtu.be/123") == "youtube"
    assert detect_platform("https://soundcloud.com/artist/track") == "soundcloud"
    assert detect_platform("https://bandcamp.com/track") == "bandcamp"

def test_load_config():
    cfg = load_config()
    assert isinstance(cfg, dict)
    assert "format" in cfg
    assert "music_dir" in cfg
