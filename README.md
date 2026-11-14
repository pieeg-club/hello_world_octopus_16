# Hello Octopus 16 — 60-Second BCI Hackathon Starter ⚡

**16 channels of 24-bit wireless EEG in a 26 mm coin-sized sensor. Zero gel, zero ear clips, zero backend required.**

Built for university hackathons — everything is hands-on and educational, starting with flashing the board's firmware right from your browser: **flash firmware → clone → stream live 16-ch EEG (or run the 250 Hz simulator) → paste a prompt into Copilot / Claude Code / Cursor → ship a working BCI app in under 60 seconds.**

> **Quick Jump:** [1. Flash & Verify (Web Tool)](#-step-1-flash--verify-octopus-16-web-flasher--cloud) · [2. Clone & Run (30s)](#-step-2-clone--run-in-30-seconds) · [3. Pick an AI Prompt & Build](#-step-3-build-your-hackathon-app-with-ai-click-a-prompt) · [4. Place Sensor on Head](#-step-4-wearing-octopus-16-hardware-cheat-sheet) · [Python Track](#-python--ml-track-bleak--numpy--csv--lsl) · [Minimal SDK Code](#-minimal-pieegjs-snippet)

---

## 🔥 Step 1: Flash & Verify Octopus 16 (Web Flasher + Cloud)

For hackathons, the entire stack is educational — start by installing the firmware onto your **Octopus 16** (Seeed XIAO ESP32-S3) and verifying the live 16-channel stream in your browser before writing a single line of code:

1. Plug your **Octopus 16** into your computer via USB-C.
2. Open the **OctoBridge Web Flasher** in **Chrome** or **Edge**:
   👉 **[https://octobridge.pieeg.com/flash](https://octobridge.pieeg.com/flash)**
3. Click **Flash**, select the USB serial port, and wait a few seconds for the firmware install to complete.
4. *(Unplug from your laptop and switch to a **5 V battery power bank** before wearing the sensor on your head!)*
5. **Instant Hardware Test:** Open **[https://cloud.pieeg.com](https://cloud.pieeg.com)** in Chrome/Edge, pair with `Octopus-16-XXXX` over Bluetooth, and confirm all 16 channels are streaming live!
   *(💡 **Important:** Click **Disconnect** or close the `cloud.pieeg.com` tab before moving to Step 2 — BLE only allows one active connection at a time!)*

> 💻 **Don't have the hardware in hand yet?** Skip straight to [Step 2](#-step-2-clone--run-in-30-seconds) and use the built-in **250 Hz Simulator**.

---

## ⚡ Step 2: Clone & Run in 30 Seconds

```bash
# 1. Clone the starter repo
git clone https://github.com/pieeg-club/hello_world_octopus_16.git
cd hello_world_octopus_16

# 2. Start a local server (Web Bluetooth requires localhost in Chrome or Edge)
npm start
# (Or without Node: python -m http.server 3000)
```

3. **Open the live 16-Channel Workbench in Chrome / Edge:**
   * 🔌 **Have the board?** Open **`http://localhost:3000`** and click **Connect Octopus 16 (BLE)** → select `Octopus-16-XXXX`.
   * 💻 **No hardware yet / coding while a teammate wears it?** Open **`http://localhost:3000/?sim=1`** to launch the **250 Hz Simulator** immediately (press `Space` = Eye Blink, `A` = Alpha Wave Boost, `C` = Jaw Clench).

---

## 🤖 Step 3: Build Your Hackathon App with AI (Click a Prompt!)

This repo is pre-wired for **GitHub Copilot, Claude Code, Cursor, and Windsurf** via [`AGENTS.md`](./AGENTS.md), [`CLAUDE.md`](./CLAUDE.md), and [`.cursorrules`](./.cursorrules) — your AI agent already knows the exact BLE UUIDs, 51-byte packet layout, 16-pin hex geometry, and 60fps zero-lag rules.

**Pick what you want to build, click the prompt, and paste it into your AI coding agent:**

| Hackathon Track | Ready-to-Paste AI Prompt | Output File |
|---|---|---|
| 🎮 **60fps BCI Arcade Game** | [**Prompt 1: Mind Shield & Blink Laser →**](./PROMPTS.md#prompt-1-from-0--60fps-bci-arcade-game-mind-shield--blink-laser) | `bci-game.html` (Alpha shield + blink laser + jaw-clench slow-mo) |
| 🎵 **Neurofeedback Synth** | [**Prompt 2: Pz Alpha WebAudio Synthesizer →**](./PROMPTS.md#prompt-2-from-0--pz-alpha-neurofeedback--binaural-webaudio-synthesizer) | `neuro-synth.html` (30s calibration wizard + Z-score ambient pad) |
| 🗺️ **16-Pin Spatial Heatmap** | [**Prompt 3: Surface Laplacian & Micro-Topography →**](./PROMPTS.md#prompt-3-from-0--high-density-16-pin-micro-topography--surface-laplacian-explorer) | `spatial-lab.html` (2D hex interpolation + Current Source Density) |
| 👀 **SSVEP / P300 Speller** | [**Prompt 4: Visual Flicker Stimulus & CSV Recorder →**](./PROMPTS.md#prompt-4-from-0--ssvep--p300-visual-stimulus--epoch-recorder-with-24414-hz-clock-compensation) | `ssvep-lab.html` (10/12/15 Hz targets + labeled trial export) |
| ⚛️ **React / Three.js Hook** | [**Prompt 5: Zero-Lag `useOctopus16` Hook →**](./PROMPTS.md#prompt-5-from-0--react--vite--threejs-high-performance-hook-useoctopus16) | `useOctopus16.ts` (250 Hz ref stream + 15 Hz React state) |

> 💡 **Want to write your own prompt?** Just start your message with:
> `"Read AGENTS.md and ./pieeg.js, then build..."`

---

## 🐍 Python & ML Track (`bleak` + `numpy` + CSV / LSL)

Prefer Python for SciPy, MNE, or PyTorch? Use [`python_quickstart.py`](./python_quickstart.py):

```bash
pip install bleak numpy

python python_quickstart.py --sim            # 1. Test immediately with 250 Hz synthetic EEG
python python_quickstart.py                  # 2. Auto-discover & stream Octopus 16 over BLE
python python_quickstart.py --csv trial.csv  # 3. Record 16-ch µV stream to CSV for ML training
```

---

## 🧠 Step 4: Wearing Octopus 16 (Hardware Cheat Sheet)

### Where to Place It on the Head
1. **Top-Back (`Pz`) — Best for Alpha Relaxation (`8–13 Hz`):** Part the hair, press the 18 spring-loaded pogo pins straight down (`90°`), hold snug with a headband, and close your eyes. Watch Alpha power surge.
2. **Back (`Oz`) — Visual Cortex & SSVEP:** Ideal for steady-state visually evoked potentials (looking at 10 Hz / 12 Hz / 15 Hz flickering targets).
3. **Forehead (`Fp1` / `Fp2`) — Blinks & EMG Game Triggers:** Zero hair parting needed; gives crisp `>120 µV` eye-blink spikes and jaw-clench bursts for instant arcade controls.

### Hardware & BLE Specs (Reference)

| Spec | Value |
|---|---|
| **Electrodes** | **18 dry spring-loaded pogo pins** (`16 signal` + `1 AINREF` + `1 GND`) in a `20 × 20 mm` hex cluster |
| **ADCs** | `2 × TI ADS131M08` (24-bit simultaneous ΔΣ, PGA gain `4`, 1.2 V ref, ~1 Hz on-chip DC block) |
| **Sample Rate** | `250 SPS` nominal (`~244.14 SPS` on 8.000 MHz ESP32 LEDC clock; live via `eeg.getStats().measuredHz`) |
| **BLE Service UUID** | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| **Notify Char UUID** | `beb5483e-36e1-4688-b7f5-ea07361b26a8` (51-byte packet: `0xA0`, counter, `16 × 3B` BE int24, `0xC0`) |

### Board LED Decoder
* **Slow 1 Hz blink:** Advertising on BLE (ready to pair)
* **Solid ON:** Connected and streaming 250 SPS
* **Fast double-blink:** ADC not detected (check that XIAO ESP32-S3 `5V/GND/3V3` pins are not seated 180° reversed!)

> ⚠️ **Safety:** Octopus 16 is not a medical device. While worn on the head, power it **only from a 5 V battery power bank**, never connected to mains power or a wall-plugged laptop.

---

## 🗂️ What's in This Repo?

| File | Purpose |
|---|---|
| [`index.html`](./index.html) | **60fps 16-Channel Workbench** — Live waveforms, FFT spectrum, 18-pin hex contact map, Laplacian toggle & CSV recorder |
| [`pieeg.js`](./pieeg.js) | **Zero-dependency Browser SDK** — Web Bluetooth, 250 Hz simulator, Hampel + Butterworth + Notch DSP, FFT & Surface Laplacian |
| [`PROMPTS.md`](./PROMPTS.md) | **Copy-Paste AI Prompt Playbook** — 5 complete prompts from 0 to full BCI app |
| [`AGENTS.md`](./AGENTS.md) | **AI Agent Ground Truth** — Hardware specs, BLE wire protocol & 60fps rules (also linked via [`CLAUDE.md`](./CLAUDE.md) & [`.cursorrules`](./.cursorrules)) |
| [`python_quickstart.py`](./python_quickstart.py) | **Python BLE Streamer** — `bleak` + `numpy` live terminal dashboard, simulator, CSV logger & LSL bridge |

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
