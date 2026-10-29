name = "dlmusic"
block_cipher = None

a = Analysis(
    ['../src/dlmusic/launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('../src/dlmusic', 'dlmusic')],
    hiddenimports=['tkinter', '_tkinter', 'customtkinter', 'yt_dlp', 'spotdl', 'platformdirs', 'mutagen', 'syncedlyrics'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dlmusic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dlmusic',
)
