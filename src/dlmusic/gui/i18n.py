TRANSLATIONS = {
    "es": {
        "title": "dlmusic — Descargador de Música",
        "urls_label": "URLs (una por línea):",
        "download_btn": "Iniciar Descargas",
        "cancel_btn": "Cancelar",
        "settings_tab": "Ajustes",
        "queue_tab": "Cola de Descargas",
        "logs_tab": "Registros",
        "output_dir": "Carpeta de salida:",
        "format": "Formato de audio:",
        "bitrate": "Bitrate:",
        "jobs": "Trabajos paralelos:",
        "lyrics": "Incrustar letras",
        "save_settings": "Guardar Ajustes",
        "settings_saved": "¡Ajustes guardados!",
        "status_idle": "Listo",
        "status_downloading": "Descargando...",
        "col_url": "URL / Canción",
        "col_platform": "Plataforma",
        "col_status": "Estado",
        "col_progress": "Progreso",
        "col_speed": "Velocidad"
    },
    "en": {
        "title": "dlmusic — Music Downloader",
        "urls_label": "URLs (one per line):",
        "download_btn": "Start Downloads",
        "cancel_btn": "Cancel",
        "settings_tab": "Settings",
        "queue_tab": "Download Queue",
        "logs_tab": "Logs",
        "output_dir": "Output folder:",
        "format": "Audio format:",
        "bitrate": "Bitrate:",
        "jobs": "Parallel jobs:",
        "lyrics": "Embed lyrics",
        "save_settings": "Save Settings",
        "settings_saved": "Settings saved!",
        "status_idle": "Idle",
        "status_downloading": "Downloading...",
        "col_url": "URL / Song",
        "col_platform": "Platform",
        "col_status": "Status",
        "col_progress": "Progress",
        "col_speed": "Speed"
    }
}

def t(key: str, lang: str = "es") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)
