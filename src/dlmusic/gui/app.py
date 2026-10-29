import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..config import load_config, save_config
from ..core.queue import DownloadManager
from .i18n import t


class DLMusicApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.lang = self.cfg.get("language", "es")
        
        ctk.set_appearance_mode(self.cfg.get("theme", "system"))
        ctk.set_default_color_theme("blue")
        
        self.title(t("title", self.lang))
        self.geometry("900x600")
        
        self.manager = None
        
        self.create_widgets()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_queue = self.tabview.add(t("queue_tab", self.lang))
        self.tab_settings = self.tabview.add(t("settings_tab", self.lang))
        self.tab_logs = self.tabview.add(t("logs_tab", self.lang))
        
        # --- Pestaña Cola ---
        self.setup_queue_tab()
        
        # --- Pestaña Ajustes ---
        self.setup_settings_tab()
        
        # --- Pestaña Logs ---
        self.setup_logs_tab()

    def setup_queue_tab(self):
        frame_top = ctk.CTkFrame(self.tab_queue)
        frame_top.pack(fill="x", padx=10, pady=10)
        
        self.lbl_urls = ctk.CTkLabel(frame_top, text=t("urls_label", self.lang))
        self.lbl_urls.pack(anchor="w", padx=5)
        
        self.txt_urls = ctk.CTkTextbox(frame_top, height=120)
        self.txt_urls.pack(fill="x", padx=5, pady=5)
        
        frame_btns = ctk.CTkFrame(self.tab_queue, fg_color="transparent")
        frame_btns.pack(fill="x", padx=10, pady=5)
        
        self.btn_download = ctk.CTkButton(frame_btns, text=t("download_btn", self.lang), command=self.start_downloads)
        self.btn_download.pack(side="left", padx=5)
        
        self.btn_cancel = ctk.CTkButton(frame_btns, text=t("cancel_btn", self.lang), fg_color="red", command=self.cancel_downloads)
        self.btn_cancel.pack(side="left", padx=5)
        
        # Lista / Área de estado
        self.txt_status = ctk.CTkTextbox(self.tab_queue, height=250)
        self.txt_status.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_status.configure(state="disabled")

    def setup_settings_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_settings)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carpeta de salida
        ctk.CTkLabel(frame, text=t("output_dir", self.lang)).pack(anchor="w", pady=2)
        dir_frame = ctk.CTkFrame(frame, fg_color="transparent")
        dir_frame.pack(fill="x", pady=2)
        
        self.ent_dir = ctk.CTkEntry(dir_frame)
        self.ent_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_dir.insert(0, self.cfg.get("music_dir", ""))
        
        ctk.CTkButton(dir_frame, text="...", width=40, command=self.browse_dir).pack(side="right")
        
        # Formato
        ctk.CTkLabel(frame, text=t("format", self.lang)).pack(anchor="w", pady=(10, 2))
        self.opt_format = ctk.CTkOptionMenu(frame, values=["m4a", "mp3", "flac", "opus"])
        self.opt_format.pack(anchor="w", pady=2)
        self.opt_format.set(self.cfg.get("format", "m4a"))
        
        # Idioma
        ctk.CTkLabel(frame, text="Idioma / Language:").pack(anchor="w", pady=(10, 2))
        self.opt_lang = ctk.CTkOptionMenu(frame, values=["es", "en"], command=self.change_language)
        self.opt_lang.pack(anchor="w", pady=2)
        self.opt_lang.set(self.lang)
        
        # Botón Guardar
        ctk.CTkButton(frame, text=t("save_settings", self.lang), command=self.save_user_settings).pack(anchor="w", pady=20)

    def setup_logs_tab(self):
        self.txt_logs = ctk.CTkTextbox(self.tab_logs)
        self.txt_logs.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_logs.configure(state="disabled")

    def log(self, msg: str):
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert("end", msg + "\n")
        self.txt_logs.see("end")
        self.txt_logs.configure(state="disabled")

    def log_status(self, msg: str):
        self.txt_status.configure(state="normal")
        self.txt_status.insert("end", msg + "\n")
        self.txt_status.see("end")
        self.txt_status.configure(state="disabled")

    def browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.ent_dir.delete(0, "end")
            self.ent_dir.insert(0, d)

    def change_language(self, new_lang):
        self.cfg["language"] = new_lang
        save_config(self.cfg)
        messagebox.showinfo("dlmusic", "Reinicia la aplicación para aplicar completamente el cambio de idioma." if new_lang == "es" else "Restart the app to fully apply language change.")

    def save_user_settings(self):
        self.cfg["music_dir"] = self.ent_dir.get()
        self.cfg["format"] = self.opt_format.get()
        save_config(self.cfg)
        messagebox.showinfo("dlmusic", t("settings_saved", self.lang))

    def start_downloads(self):
        urls_raw = self.txt_urls.get("1.0", "end").strip()
        if not urls_raw:
            return
        urls = [u.strip() for u in urls_raw.split("\n") if u.strip()]
        
        self.manager = DownloadManager(max_workers=self.cfg.get("jobs", 4))
        self.log_status(f"Iniciando descarga de {len(urls)} URLs...")
        
        def run():
            for url in urls:
                self.manager.download_url(url, self.cfg, lambda u, ev: self.after(0, lambda: self.on_progress(u, ev)))
            self.after(0, lambda: self.log_status("¡Todas las descargas finalizadas!"))

        threading.Thread(target=run, daemon=True).start()

    def cancel_downloads(self):
        if self.manager:
            self.manager.cancel_all()
            self.log_status("Cancelando descargas...")

    def on_progress(self, url: str, ev):
        if ev.status == "downloading":
            self.log_status(f"[{ev.status.upper()}] {ev.artist} - {ev.title} ({ev.percent:.1f}%) {ev.speed}")
        elif ev.status == "finished":
            self.log_status(f"[✓] Completado: {ev.title}")
        elif ev.status == "error":
            self.log_status(f"[✗] Error en {url}: {ev.error_message}")
            self.log(f"Error {url}: {ev.error_message}")
