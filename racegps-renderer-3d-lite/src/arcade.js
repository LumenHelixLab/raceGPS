/**
 * RaceGPS Arcade "Midnight Run" Engine
 * Handles Web Audio API engine synth, Arcade HUD, Nitro boost, and camera dynamics.
 */

class MidnightArcadeEngine {
  constructor() {
    this.audioCtx = null;
    this.oscillator = null;
    this.gainNode = null;
    this.isMuted = false;
    this.nitro = 100;
    this.gear = 1;
  }

  initAudio() {
    if (this.audioCtx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    this.audioCtx = new AudioContext();

    this.oscillator = this.audioCtx.createOscillator();
    this.gainNode = this.audioCtx.createGain();

    this.oscillator.type = 'sawtooth';
    this.oscillator.frequency.setValueAtTime(60, this.audioCtx.currentTime);
    this.gainNode.gain.setValueAtTime(0.05, this.audioCtx.currentTime);

    this.oscillator.connect(this.gainNode);
    this.gainNode.connect(this.audioCtx.destination);
    this.oscillator.start();
  }

  updateEngineSound(speedMph) {
    if (!this.audioCtx || this.isMuted) return;

    // Compute synthetic gear (1 to 6)
    if (speedMph < 25) this.gear = 1;
    else if (speedMph < 45) this.gear = 2;
    else if (speedMph < 70) this.gear = 3;
    else if (speedMph < 95) this.gear = 4;
    else if (speedMph < 120) this.gear = 5;
    else this.gear = 6;

    // Frequency mapped to speed & gear shift loops
    const gearBaseSpeed = (speedMph % 25) * 4;
    const freq = 50 + gearBaseSpeed + this.gear * 15;
    this.oscillator.frequency.setTargetAtTime(freq, this.audioCtx.currentTime, 0.05);
  }

  triggerNitro() {
    if (this.nitro > 10) {
      this.nitro -= 15;
      return true; // Nitro active
    }
    return false;
  }

  rechargeNitro() {
    if (this.nitro < 100) this.nitro += 0.2;
  }
}

window.MidnightArcadeEngine = MidnightArcadeEngine;
