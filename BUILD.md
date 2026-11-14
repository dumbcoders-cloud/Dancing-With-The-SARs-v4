# Dancing with the SARs — Build Log

## Project overview

A NASA Space Apps Challenge hackathon prototype for exploring simulated surface change over time. The desktop app combines a local FastAPI JSON API, a Flask/Jinja web interface, a PyDeck/Deck.gl map, and a PyWebView window. Study options currently include Jakobshavn Glacier, Thwaites Glacier, Kīlauea Volcano, and the San Andreas Fault. **The map uses actual NASA MODIS Terra imagery for context; displacement values and vectors remain simulated and are not NISAR measurements.**

## Current technology stack

- **API/runtime:** FastAPI, Uvicorn
- **Web interface/static files:** Flask, Jinja templates, HTML/CSS/JavaScript
- **Flask bridge:** a2wsgi WSGI middleware mounted by FastAPI
- **Map:** PyDeck and Deck.gl; date-matched NASA GIBS MODIS Terra tiles with CARTO fallback basemap
- **Desktop:** PyWebView with Microsoft Edge WebView2 on Windows
- **Build and icon:** PyInstaller and Pillow
- **Data:** deterministic Python-generated synthetic observations; no live SAR products

## Completed Steps

- **Step 1 — Initialize BUILD.md:** created the engineering log before implementation and maintained the roadmap as the project stack changed.
- **Step 2 — Project scaffolding:** established the Python package, `src/dancing_sars/`, Flask templates/static assets, `assets/`, requirements files, and source entry point.
- **Step 3 — Desktop build configuration:** configured PyInstaller one-file, windowed packaging for Windows; added PyWebView launcher, icon generation, and local build instructions. Android and Linux desktop packaging remain future work.
- **Step 4 — Map and time-series prototype:** implemented a dark-themed interactive Deck.gl map, deterministic sample pipeline with 63 points over 13 quarterly dates, metrics, history plot, timeline playback, layer controls, and CSV export.
- **Step 5 — Expanded study areas and themes:** added four selectable synthetic scenes (Jakobshavn, Thwaites, Kīlauea, San Andreas), responsive light/dark interface themes, and persistent theme selection.
- **Step 6 — FastAPI and Flask server:** replaced the Streamlit runtime with FastAPI endpoints and a Flask/Jinja UI mounted through a2wsgi. Added health, study, history, observation, generated map, and CSV endpoints. Updated the development and PyWebView launchers.
- **Step 7 — Documentation and packaging:** revised `README.md`, `PROJECT_GUIDE.md`, and `HACKATHON_TALK_TRACK.txt`; updated dependencies and PyInstaller configuration; regenerated the app `.ico` and PNG preview.
- **Step 8 — NASA data integration:** added actual date-matched MODIS Terra Corrected Reflectance True Color tiles from NASA GIBS as a map layer, with an on/off control and visible source attribution. The NASA imagery is optical context; displacement vectors and metrics remain simulated. Updated submission/resource documentation accordingly.
- **Step 9 — Repair blank NASA map rendering:** replaced PyDeck's unsupported `renderSubLayers` callback expression with 15 declarative NASA GIBS `BitmapLayer` tiles around the selected study area. The map now keeps its CARTO basemap and simulated overlays visible through polar winter, when MODIS visible-light scenes are effectively black; the UI explains this fallback.
- **API smoke check:** passed local HTTP checks for health, Flask page and static files, all four studies, all 13 dates and 63 samples, light-themed map HTML, and CSV export.
- **NASA GIBS integration check:** a date-specific MODIS Terra tile returned HTTP 200 (`image/jpeg`) with browser CORS enabled. All 52 area/date observation API responses and four GIBS-enabled map HTML responses passed; disabling the NASA layer removes its tile layer from the generated map.
- **Source map-render check:** Edge rendered the dashboard with two Deck canvases, a working CARTO basemap, and sample overlays with zero JavaScript exceptions. Moving the timeline to July loaded 15 date-matched NASA tiles; all returned HTTP 200. The January Jakobshavn scene rendered the basemap and overlays without the black polar-night raster.
- **Windows build:** PyInstaller 6.22.3 completed successfully on Windows 11 / Python 3.14.6 on 2026-11-15. Output: `dist/DancingWithTheSARs.exe` (38,241,628 bytes; about 36.5 MiB), with the application icon embedded.
- **Packaged EXE smoke check:** launched the rebuilt executable and confirmed its titled PyWebView window and local API health endpoint. All four study areas returned their 13-date histories, representative map routes in both themes, and CSV export. Edge rendered the map route served by the EXE; the January fallback worked, while the July scene requested 15 NASA tiles (all HTTP 200) with zero JavaScript or image-load errors.
- **NASA raster checks:** representative NASA GIBS tiles for Jakobshavn, Thwaites, Kīlauea, and San Andreas returned HTTP 200 (`image/jpeg`) with `Access-Control-Allow-Origin: *`.
- **Prior packaged desktop runtime smoke check:** the preceding FastAPI/Flask build opened its titled PyWebView window after Smart App Control was disabled; health, dashboard, study, map, and CSV routes passed.
- **Prior continuous runtime soak:** before NASA imagery integration, the packaged app ran for 5 minutes across 369 cycles and 1,680 HTTP requests with zero failures. Maximum observed request latency was 77 ms (37 ms p95).
- **Source/package checks:** JavaScript syntax and Python bytecode compilation completed without errors. The built executable archive contains the FastAPI module, Flask template/static assets, and generated icon. The Linux packaging script was aligned with the new dependencies but remains unvalidated.

## Planned Future Steps

- Check the app on a second clean Windows machine with the Microsoft Edge WebView2 Runtime before sharing broadly.
- Sign the executable and follow the target organization's allow-listing/distribution process if required.
- Replace synthetic displacement values with a validated NASA surface-displacement product such as OPERA DISP-S1 (Sentinel-1-derived), and later integrate NISAR displacement products when available; preserve acquisition metadata, coordinate reference systems, units, provenance, uncertainty, and processing lineage.
- Add additional science workflows such as forest dynamics and agricultural change when suitable data and methods are available.
- Choose and implement an Android architecture before adding an APK build; the current project does not produce an Android package.
- Configure and validate a Linux PyWebView backend before claiming Linux desktop packaging support.
- Continue UI/accessibility polish and test the theme and timeline on small screens.

## Build/run quick reference

- Web app: `python -m pip install -r requirements.txt`, then `python app.py` and open `http://127.0.0.1:8501`.
- Windows desktop from source: `python -m pip install -r requirements-desktop.txt`, then `python scripts/launch_desktop.py`.
- Windows executable: run `scripts/build_windows.ps1` from PowerShell. The output is `dist/DancingWithTheSARs.exe`.
- Full component descriptions, API routes, run instructions, advantages, trade-offs, and troubleshooting are in `PROJECT_GUIDE.md`.
