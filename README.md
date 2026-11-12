# Hello Octopus 16 — 60-Second University BCI Hackathon Starter

**16 channels of 24-bit wireless EEG in a 26 mm coin-sized sensor. Zero gel, zero ear clips, zero backend required.**

This repository is designed so university hackathon teams can clone, stream live 16-channel brainwaves (or use the built-in 250 Hz simulator), and build high-performance BCI games, neurofeedback synths, or ML pipelines with **AI coding agents (GitHub Copilot, Claude Code, Cursor)** in under **60 seconds**.

---

## 🚀 Start in 60 Seconds

### Option A: Browser (Zero Install — `pieeg.js` + 60fps Canvas Workbench)
1. Serve this folder over `localhost` (Web Bluetooth requires `localhost` or `HTTPS` in **Chrome** or **Edge**):
   ```bash
   npx serve -l 3000 .
   # OR with Python:
   python -m http.server 3000
   ```
2. Open **`http://localhost:3000`** (or **`http://localhost:3000/?sim=1`** to auto-launch the 250 Hz simulator).
3. Click **Connect Octopus 16 (BLE)** and select `Octopus-16-XXXX` — or click **Start 250 Hz Simulator** so all 4 teammates can code and test even while 1 person wears the sensor!

### Option B: Python (`bleak` + `numpy` + CSV / LSL)
```bash
pip install bleak numpy
python python_quickstart.py --sim            # Test immediately without hardware
python python_quickstart.py                  # Auto-discover Octopus 16 over BLE
python python_quickstart.py --csv trial.csv  # Record 16-ch µV stream to CSV
```

---

## 🤖 Built for AI & Coding Agents (`AGENTS.md` + `PROMPTS.md`)

Most AI assistants hallucinate BLE UUIDs or write slow `250 Hz` React `setState` loops that freeze the browser. This boilerplate fixes that out of the box:

* **[`AGENTS.md`](./AGENTS.md)** / **[`CLAUDE.md`](./CLAUDE.md)** / **[`.cursorrules`](./.cursorrules)**: Pre-loads your AI assistant with the exact Octopus 16 BLE UUIDs, 51-byte ADS131M08 packet format, 16-pin hexagonal `(x, y)` mm coordinates, and strict 60fps zero-GC performance rules.
* **[`PROMPTS.md`](./PROMPTS.md)**: Copy-paste **"From 0 to Full BCI App"** prompts (60fps BCI arcade game, Pz Alpha WebAudio synthesizer, 16-pin Surface Laplacian micro-topography explorer, SSVEP/ERP experiment runner, and React/Three.js hook).

---

## 🧠 Hardware Cheat Sheet (Octopus 16)

| Spec | Value |
|---|---|
| **Electrodes** | **18 dry spring-loaded pogo pins** (`16 signal` + `1 AINREF` + `1 GND`) in one `20 × 20 mm` hexagonal cluster |
| **ADCs** | `2 × TI ADS131M08` (24-bit simultaneous ΔΣ, PGA gain `4`, 1.2 V ref, ~1 Hz on-chip DC block) |
| **Sample Rate** | `250 SPS` nominal (`~244.14 SPS` on boards clocked via 8.000 MHz ESP32 LEDC; tracked live via `eeg.getStats().measuredHz`) |
| **BLE Service UUID** | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| **Notify Char UUID** | `beb5483e-36e1-4688-b7f5-ea07361b26a8` (51-byte packet: `0xA0`, counter, `16 × 3B` BE int24, `0xC0`) |

### Where to Place Octopus 16 on the Head
1. **Top-Back (`Pz`) — Default for Alpha Waves (`8–13 Hz`):** Part the hair, press the 18 pogo pins straight down (`90°`), hold with a headband, and close your eyes. Watch Alpha power surge.
2. **Back (`Oz`) — Visual Cortex & SSVEP:** Ideal for steady-state visually evoked potentials (flickering targets at 10 Hz / 12 Hz / 15 Hz).
3. **Forehead (`Fp1` / `Fp2`) — Blinks & EMG Game Triggers:** Zero hair parting needed; produces crisp `>120 µV` eye-blink spikes and jaw-clench bursts for hands-free controllers.

### Board LED Decoder
* **Slow 1 Hz blink:** Advertising on BLE (ready to connect)
* **Solid ON:** Connected and streaming 250 SPS
* **Fast double-blink:** ADC not detected (check that XIAO ESP32-S3 `5V/GND/3V3` pins are not seated 180° reversed!)

> ⚠️ **Safety:** Octopus 16 is not a medical device. While worn on the head, power it **only from a 5 V battery power bank**, never connected to mains power or a wall-plugged laptop.

---

## 📦 Minimal `pieeg.js` Snippet

```html
<script src="./pieeg.js"></script>
<script>
  const eeg = new PiEEG({ filter: { notch: 50, bandpass: { low: 1, high: 40 } } });

  eeg.onBandPowers((powers, spectrum) => {
    console.log('Alpha (µV²):', powers.Alpha.toFixed(1), 'Peak Hz:', spectrum.dominantFreq.toFixed(1));
  });

  // Connect real hardware (must be inside a click handler) OR start simulator:
  document.getElementById('btn').onclick = () => eeg.connectBLE({ device: 'octopus-16' });
  // await eeg.connectSimulator({ device: 'octopus-16' });
</script>
```
