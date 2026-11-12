# PROMPTS.md — "From 0 to Working BCI App" AI Prompt Playbook (`pieeg.js` + Octopus 16)

Drop any of these copy-paste prompts into **GitHub Copilot Chat, Claude Code, Cursor, or Windsurf**. Because this repo includes [`AGENTS.md`](./AGENTS.md) and [`./pieeg.js`](./pieeg.js), your AI assistant already has the exact hardware specs, 51-byte BLE decoder, 16-pin hexagonal geometry, and 60fps performance rules!

---

## Prompt 1: From 0 → 60fps BCI Arcade Game ("Mind Shield & Blink Laser")

```text
Read AGENTS.md and ./pieeg.js. Build a complete, single-file 60fps HTML5 Canvas game (`bci-game.html`) powered by Octopus 16 and `./pieeg.js`:
1. Connection Bar: "Connect Octopus 16 (BLE)" (`eeg.connectBLE({ device: 'octopus-16' })`) AND "250 Hz Simulator Mode" (`eeg.connectSimulator({ device: 'octopus-16' })`) with keyboard shortcuts (`A` = toggle Eyes Closed Alpha, `Space` = Blink, `C` = Jaw Clench).
2. Mechanics:
   - The player ship has an energy shield whose radius and regeneration rate scale with live Alpha relaxation (`eeg.getRelaxationIndex()`), gated so jaw-clench EMG artifacts (`Gamma` spike or RMS > 90 µV) don't falsely charge the shield.
   - Eye Blinks (peak amplitude > 115 µV across frontal/global channels with a 350 ms cooldown) fire a shockwave pulse that clears incoming asteroids.
   - Jaw Clench (high-frequency RMS burst) triggers a 2-second time-slow overdrive.
3. HUD: Show a compact 18-pin hexagonal contact quality mini-map (`PiEEG.OCTOPUS_16_PINS` + `eeg.getContactQuality()`) in the corner so the player knows all pogo pins have scalp contact.
4. Performance: Zero DOM updates inside `eeg.onData()`. Do all rendering in a single `requestAnimationFrame` loop.
```

---

## Prompt 2: From 0 → Pz Alpha Neurofeedback & Binaural WebAudio Synthesizer

```text
Read AGENTS.md and ./pieeg.js. Create a neurofeedback soundscape app (`neuro-synth.html`) for an Octopus 16 placed over Pz:
1. Support both `eeg.connectBLE({ device: 'octopus-16' })` and `eeg.connectSimulator({ device: 'octopus-16' })`.
2. Calibration Wizard (30 seconds):
   - Step 1: Record 15 seconds of Eyes-Open baseline Alpha power (`8-13 Hz`) at Pz and compute mean + standard deviation.
   - Step 2: Record 15 seconds of Eyes-Closed Alpha power and compute the user's Individual Alpha Peak Frequency (`spectrum.dominantFreq` between 8 and 13 Hz).
3. WebAudio Engine:
   - Synthesize a warm ambient pad using WebAudio oscillators + lowpass filter whose cutoff frequency and harmonic richness open up smoothly as the user's real-time Alpha Z-score rises above their Eyes-Open baseline.
   - Automatically mute/duck the reward chime if `eeg.getContactQuality()` detects railed pins (>150 µV RMS) or blink/muscle artifacts.
4. Visuals: Render a 60fps Canvas aurora visualizer + live Individual Alpha Peak tracker.
```

---

## Prompt 3: From 0 → High-Density 16-Pin Micro-Topography & Surface Laplacian Explorer

```text
Read AGENTS.md and ./pieeg.js. Build a spatial neuroscience tool (`spatial-lab.html`) that exploits Octopus 16's 20×20 mm hexagonal pogo-pin array (`PiEEG.OCTOPUS_16_PINS`):
1. Connect via `connectBLE({ device: 'octopus-16' })` or `connectSimulator({ device: 'octopus-16' })`.
2. Render a high-resolution 2D interpolated heatmap (Inverse Distance Weighting across the 16 `(x, y)` mm pin coordinates inside the 26 mm circle) at 60fps on `<canvas>`.
3. Allow switching the heatmap source between:
   - Instantaneous potential (µV)
   - Surface Laplacian / Current Source Density (`eeg.computeLaplacian(channels)`)
   - Per-channel Alpha (8–13 Hz), Theta (4–8 Hz), or Beta (13–30 Hz) power (`eeg.getChannelBandPowers()`)
   - Pin-to-Scalp Contact Quality RMS (`eeg.getContactQuality()`)
4. Allow clicking any of the 16 pins on the hex map to inspect its solo time-domain waveform, PSD spectrum, and nearest hex neighbors.
```

---

## Prompt 4: From 0 → SSVEP / P300 Visual Stimulus & Epoch Recorder (with 244.14 Hz Clock Compensation)

```text
Read AGENTS.md and ./pieeg.js. Build an SSVEP + ERP experiment runner (`ssvep-lab.html`) for Octopus 16 placed over Oz / Pz:
1. Render 3 flickering SSVEP target boxes on screen using `requestAnimationFrame` at 10 Hz, 12 Hz, and 15 Hz.
2. Stream 16-channel EEG from Octopus 16 (`connectBLE` or `connectSimulator` with `eeg.triggerSimEvent('ssvep', freq)`).
3. Account for the Octopus 16 clock note in AGENTS.md (use `eeg.getStats().measuredHz` or arrival timestamps for exact epoch alignment).
4. Compute real-time SNR at 10 Hz, 12 Hz, and 15 Hz across the 16 channels (after `eeg.computeLaplacian`) to highlight which box the user is looking at, and include a "Download Labeled Trials CSV" button for offline Python/MNE analysis.
```

---

## Prompt 5: From 0 → React / Vite / Three.js High-Performance Hook (`useOctopus16`)

```text
Read AGENTS.md and ./pieeg.js. Create a production-ready React hook `useOctopus16.ts` and a demo component that connects to Octopus 16 WITHOUT causing 250 Hz React re-render lag:
1. Keep the `PiEEG` instance and 250 Hz `onData` stream in a `useRef` (never call `useState` inside `onData`).
2. Expose a `subscribeSamples(cb)` ref-callback for 60fps `<canvas>` or Three.js `useFrame` consumers.
3. Update React state (`bandPowers`, `contactQuality`, `stats`) ONLY inside `eeg.onBandPowers` at 10–15 Hz.
4. Include both `connectBLE()` and `connectSimulator()` actions.
```
