# AGENTS.md

Repo root: this folder (`DLMUSIC/`). A single Bash CLI: `dlmusic.sh` (v2.0.0) + `README.md`.

## What this is
- One Bash script. **No build system, no test suite, no CI.**
- Auto-routes URLs: `spotdl` for Spotify, `yt-dlp` for YouTube/YouTube Music/SoundCloud/Bandcamp and other supported sites.
- Repo: remote `Cybort8/dlmusic-cli`, branch `main`. The git root was moved here from the parent `Dev/`.
- Sibling folders (`../CRM`, `../crm-mic`, `../Formulario`, `../clip-counter`) are unrelated projects — do not touch them.

## Verify changes
- Syntax: `bash -n dlmusic.sh`
- `./dlmusic.sh --help` / `--version`
- Real smoke test (needs network + ffmpeg): `./dlmusic.sh -n -o /tmp/opencode/t -f m4a "<youtube-or-spotify-url>"` then inspect `/tmp/opencode/t`.
- Spotify path only: add `-e spotdl`.
- Tests pollute the duplicate archives in `~/.cache/dlmusic/`; clean up with `rm -rf ~/.cache/dlmusic /tmp/opencode/t*` afterwards.

## Gotchas (verified)
- `spotdl` 4.5.2 rejects `--embed-metadata`/`--embed-cover` (it embeds by default) and has no `--lyrics auto` (valid: `genius musixmatch azlyrics synced`).
- `spotdl` output template uses `{output-ext}`, **not** `{ext}` (the latter is written literally).
- `yt-dlp` output templates support fallbacks: `%(artist,uploader|Unknown Artist)s`.
- Max-quality rule: choose `-f` whose container matches the target so `-x --audio-format` copies instead of re-encoding (yt-dlp logs `Not converting audio … already in target format`). Implemented by `ytdlp_format_selector`.
- Default output is `$HOME/Music/Dilan` in the working copy, but `README.md` still documents `$HOME/Music` — reconcile when editing defaults.
- On Arch, install spotdl with `python3 -m pip install --user --break-system-packages spotdl` (plain `pip install` is blocked by PEP 668).

## Publishing
- Push to `main`. GitHub requires a PAT with **Contents: Read and write** on `Cybort8/dlmusic-cli`; never hardcode or commit tokens.
