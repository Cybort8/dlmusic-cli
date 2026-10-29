# AGENTS.md

Repo root: this folder (`DLMUSIC/`). Python package `dlmusic` (v2.1.0) + legacy `dlmusic.sh` wrapper.

## What this is
- Python project with a CustomTkinter GUI and a CLI (`--cli`). Source under `src/dlmusic/`.
- Auto-routes URLs: spotdl for Spotify, yt-dlp for YouTube/YT Music/SoundCloud/Bandcamp and more.
- Repo: remote `Cybort8/dlmusic-cli`, branch `main`.

## Developer commands
- Install (editable): `python -m pip install -e .[dev]`
- Tests: `pytest`
- Lint: `ruff check src tests`
- Types: `MYPYPATH=src mypy --namespace-packages src`
- Run GUI: `python -m dlmusic`
- Run CLI: `python -m dlmusic --cli <url> ...`
- Build (onedir): `python build/build.py` (requires `tk` installed: `sudo pacman -S tk` on Arch)
- Legacy wrapper: `./dlmusic.sh`

## Verify changes
- `bash -n dlmusic.sh`
- `python -m dlmusic --cli --version`
- `pytest`
- Real smoke test: `python -m dlmusic --cli -f m4a -o /tmp/opencode/t "<youtube-or-spotify-url>"` then inspect `/tmp/opencode/t`.
- Tests pollute duplicate archives in `~/.cache/dlmusic/`; clean up with `rm -rf ~/.cache/dlmusic /tmp/opencode/t*` afterwards.

## Gotchas (verified)
- `tkinter` is not installed on the dev host (Python 3.14 without tk); build/CI install it. GUI cannot run locally until `sudo pacman -S tk`.
- `yt-dlp` needs a JS runtime (Deno); `find_binary("deno")` returns the path or falls back to `deno` from PATH. In CI, bundle deno into `assets/`.
- spotdl 4.5.2+ rejects `--embed-metadata`/`--embed-cover` (embeds by default); no `--lyrics auto` (valid: genius musixmatch azlyrics synced); output template uses `{output-ext}`, not `{ext}`.
- yt-dlp `js_runtimes` must be a dict: `{'deno': {'path': ...}}`.
- Default output is `~/Music/Dilan` (config default); README documents `~/Music`.
- On Arch, install spotdl with `python3 -m pip install --user --break-system-packages spotdl`.

## Publishing
- Push to `main`. GitHub requires a PAT with **Contents: Read and write** on `Cybort8/dlmusic-cli`; never hardcode or commit tokens.
- Releases are produced by `.github/workflows/release.yml` on tags `v*`.