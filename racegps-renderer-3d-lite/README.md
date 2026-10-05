# RaceGPS Renderer 3D Lite 🏎️💨

> **Simple, fast, modular, and browser-first 3D map & telemetry renderer.**

`RaceGPS Renderer 3D Lite` is built to deliver real-time 3D racing track visualization and telemetry overlays directly in the browser without requiring heavy GIS pipelines or complex native software dependencies.

---

## 🏗️ Core Architecture & Tech Stack

* **[MapLibre GL JS](https://maplibre.org/) (v4.7.1)**: High-performance WebGL 3D map rendering engine supporting pitch, bearing, terrain elevation, and custom style layers.
* **[PMTiles](https://github.com/protomaps/pmtiles)**: Cloud-native, single-file serverless tile protocol for serving global vector/raster terrain data efficiently.
* **[Babylon.js](https://www.babylonjs.com/)**: Fast WebGL 3D game engine for rendering 3D car models, animated track lines, and camera chase dynamics.
* **Telemetry Processing Engine**: Native JS module for parsing GPX / NMEA / GeoJSON coordinate streams, calculating speed (MPH/KPH), altitude, heading, and lateral G-force in real-time.

---

## 🚀 Key Features

* **3D Chase Cam & Top-Down Modes**: Dynamic camera transitions following the vehicle bearing and elevation along the track.
* **Live Telemetry HUD**: Glassmorphic dark-mode HUD displaying real-time Speed, Lap Time (MM:SS.ms), Altitude, and Lateral G-Force.
* **Playback Rate Selector**: Variable rate playback (1x, 2x, 5x) for reviewing racing laps.
* **Zero Infrastructure Overhead**: Runs 100% on the frontend without requiring a specialized rendering backend.

---

## 📂 Repository Structure

```
racegps-renderer-3d-lite/
├── index.html          # Main HTML5 Web App Entrypoint
├── package.json        # Node.js Package Specs & Dependencies
├── README.md           # Documentation & Architecture
└── src/
    ├── styles.css      # Glassmorphism UI & HUD Styling
    ├── telemetry.js   # Telemetry Parser & Calculation Engine
    └── renderer.js    # MapLibre + PMTiles + Babylon.js Integration
```

---

## 💻 Local Quickstart

Run a local HTTP server using Python or Node.js:

```bash
# Python 3
python3 -m http.server 8080

# Or using Node / npx
npx http-server -p 8080
```

Open `http://localhost:8080` in your web browser.

---

## 📜 License

MIT License © 2026 Christopher Gordon Phillips ([LumenHelixLab](https://github.com/LumenHelixLab))
