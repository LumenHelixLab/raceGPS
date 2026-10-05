/**
 * RaceGPS 3D Lite Renderer - Midnight Run Arcade Edition
 * Street-Level Driver Perspective + GPS Route Overlay
 */

document.addEventListener("DOMContentLoaded", () => {
  const telemetry = new window.TelemetryEngine();
  const arcade = new window.MidnightArcadeEngine();
  const trackData = telemetry.loadSyntheticTrack("monaco");

  // DOM Metrics
  const valSpeed = document.getElementById("val-speed");
  const valTime = document.getElementById("val-time");
  const valGear = document.getElementById("val-gear");
  const valGForce = document.getElementById("val-gforce");
  const nitroFill = document.getElementById("nitro-fill");
  const btnPlayPause = document.getElementById("btn-play-pause");
  const btnReset = document.getElementById("btn-reset");
  const btnNos = document.getElementById("btn-nos");
  const selectRate = document.getElementById("playback-rate");
  const selectCamera = document.getElementById("camera-view");

  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);

  const startPoint = trackData[0];

  // MapLibre GL JS Dark Night Theme
  const map = new maplibregl.Map({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/dark",
    center: [startPoint.lng, startPoint.lat],
    zoom: 18.8, // Street Level First-Person Perspective
    pitch: 85,  // Driver cockpit look-ahead angle
    bearing: startPoint.heading || 0,
    maxPitch: 88
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }));
  const buildingGen = new window.ProceduralBuildingGenerator(map);

  map.on("load", () => {
    buildingGen.enableVector3DBuildings();

    // Glowing Synthwave Track Line Overlay
    const geojsonLine = {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: trackData.map((pt) => [pt.lng, pt.lat, pt.alt])
      }
    };

    map.addSource("track-path", {
      type: "geojson",
      data: geojsonLine
    });

    // Glowing Neon Halo Layer
    map.addLayer({
      id: "track-halo",
      type: "line",
      source: "track-path",
      paint: {
        "line-color": "#ff007f",
        "line-width": 14,
        "line-blur": 6,
        "line-opacity": 0.8
      }
    });

    // Core Neon Track Line
    map.addLayer({
      id: "track-line",
      type: "line",
      source: "track-path",
      paint: {
        "line-color": "#00f0ff",
        "line-width": 6,
        "line-opacity": 1.0
      }
    });

    // Vehicle Driver Position Marker
    map.addSource("vehicle-marker", {
      type: "geojson",
      data: {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [startPoint.lng, startPoint.lat]
        }
      }
    });

    map.addLayer({
      id: "vehicle-point",
      type: "circle",
      source: "vehicle-marker",
      paint: {
        "circle-radius": 12,
        "circle-color": "#ff007f",
        "circle-stroke-width": 3,
        "circle-stroke-color": "#00f0ff"
      }
    });
  });

  // Telemetry Frame Callback
  telemetry.subscribe((point) => {
    if (!point) return;

    // Arcade Sound Engine Update
    arcade.updateEngineSound(point.speedMph);
    arcade.rechargeNitro();
    if (nitroFill) nitroFill.style.width = `${arcade.nitro}%`;

    // HUD Update
    valSpeed.textContent = point.speedMph;
    valGForce.textContent = point.gForce >= 0 ? `+${point.gForce}` : `${point.gForce}`;
    if (valGear) valGear.textContent = arcade.gear;

    const totalSeconds = Math.floor(point.timestamp / 1000);
    const mins = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const secs = String(totalSeconds % 60).padStart(2, "0");
    const ms = String(Math.floor((point.timestamp % 1000) / 10)).padStart(2, "0");
    valTime.textContent = `${mins}:${secs}.${ms}`;

    // Update Vehicle Coordinate
    const vehicleSource = map.getSource("vehicle-marker");
    if (vehicleSource) {
      vehicleSource.setData({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [point.lng, point.lat]
        }
      });
    }

    // Camera Modes
    const camMode = selectCamera ? selectCamera.value : "driver";
    if (camMode === "driver") {
      // Driver Street Level First-Person Perspective
      map.easeTo({
        center: [point.lng, point.lat],
        bearing: point.heading,
        pitch: 85,
        zoom: 18.8,
        duration: 180,
        easing: (t) => t
      });
    } else if (camMode === "chase") {
      map.easeTo({
        center: [point.lng, point.lat],
        bearing: point.heading,
        pitch: 70,
        zoom: 17.2,
        duration: 180,
        easing: (t) => t
      });
    } else if (camMode === "topdown") {
      map.easeTo({
        center: [point.lng, point.lat],
        pitch: 0,
        zoom: 16.0,
        duration: 180,
        easing: (t) => t
      });
    }
  });

  // Playback Loop Controls
  let timerId = null;
  function startPlayback() {
    arcade.initAudio();
    if (timerId) clearInterval(timerId);
    const interval = Math.max(50, 200 / parseFloat(selectRate.value));
    timerId = setInterval(() => {
      telemetry.nextFrame();
    }, interval);
  }

  function stopPlayback() {
    if (timerId) clearInterval(timerId);
    timerId = null;
  }

  btnPlayPause.addEventListener("click", () => {
    telemetry.isPlaying = !telemetry.isPlaying;
    if (telemetry.isPlaying) {
      btnPlayPause.textContent = "Pause Run";
      btnPlayPause.classList.replace("primary", "secondary");
      startPlayback();
    } else {
      btnPlayPause.textContent = "Start Run";
      btnPlayPause.classList.replace("secondary", "primary");
      stopPlayback();
    }
  });

  btnReset.addEventListener("click", () => {
    telemetry.isPlaying = false;
    stopPlayback();
    telemetry.currentIndex = 0;
    btnPlayPause.textContent = "Start Run";
    btnPlayPause.classList.replace("secondary", "primary");
    const firstPoint = telemetry.getCurrentPoint();
    telemetry.notify(firstPoint);
  });

  if (btnNos) {
    btnNos.addEventListener("click", () => {
      arcade.triggerNitro();
    });
  }

  selectRate.addEventListener("change", () => {
    if (telemetry.isPlaying) startPlayback();
  });
});
