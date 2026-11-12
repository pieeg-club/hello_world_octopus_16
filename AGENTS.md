# AGENTS.md — AI & Coding Agent Context for Octopus 16 (`hello_world_octopus_16`)

> **READ THIS FIRST (For GitHub Copilot, Claude Code, Cursor, Windsurf, and LLM Agents):**
> This repository is the official **60-Second University BCI Hackathon Starter** for **Octopus 16** by [PiEEG](https://pieeg.com). When a user asks you to build a game, neurofeedback experience, classifier, visualizer, or research tool, follow the hardware facts, API contracts, and **strict real-time performance rules** in this document.

---

## 1. What is Octopus 16? (Hardware Ground Truth)

Octopus 16 is a **coin-sized (26.0 mm round, 4-layer) wireless 16-channel EEG sensor** with **18 built-in dry spring-loaded pogo-pin electrodes** (`⌀ 4 × 11 mm`, `~5.38 mm` hexagonal pitch, `~20.3 × 20.3 mm` total array footprint):
- **16 Signal Pins (`CH1`–`CH16`)** + **1 Reference (`AINREF`)** + **1 Ground (`GND`)** all in the **same 2 × 2 cm cluster**.
- **No gel, no cap, no ear clips.** The entire montage sits on one localized scalp spot (e.g., `Pz` for Alpha 8–13 Hz, `Oz` for visual/SSVEP, `Fp1/Fp2` for blink & forehead EMG triggers, `Cz` for sensorimotor rhythms).
- **ADCs:** 2 × Texas Instruments **ADS131M08** (24-bit simultaneous-sampling ΔΣ ADCs, 8 channels each, internal 1.2 V ref, PGA gain = 4, on-chip ~1 Hz DC-block filter enabled).
  - `CH1`–`CH8` (indices `0..7`) = ADC 1
  - `CH9`–`CH16` (indices `8..15`) = ADC 2
- **MCU & Radio:** Seeed Studio **XIAO ESP32-S3** streaming over **Bluetooth Low Energy 5 (BLE)**.
- **Safety Invariant:** Octopus 16 is **not a medical device**. When worn on the head, it MUST be powered **exclusively from a 5 V battery power bank**, never plugged into a wall charger or mains-connected laptop USB.

---

## 2. BLE Protocol & Wire Format (Do Not Hallucinate UUIDs!)

If writing custom Web Bluetooth or Python `bleak` code, use these exact verified identifiers:

| Parameter | Value |
|---|---|
| **Advertised Name** | `Octopus-16-XXXX` (also match `Octopos`, `bioron`, `PiEEG`, or by Service UUID) |
| **BLE Service UUID** | `4fafc201-1fb5-459e-8fcc-c5c9c331914b` |
| **Data Notify Char UUID** | `beb5483e-36e1-4688-b7f5-ea07361b26a8` |
| **Command Write Char UUID** | `c0de0001-36e1-4688-b7f5-ea07361b26a8` (register bridge: 1B read / 3B write / 5B masked write) |
| **Packet Size** | **51 bytes** per notification (1 sample × 16 channels) |
| **Nominal Sample Rate** | **250 SPS** (`OSR_16384`) |
| **Actual Clock Note** | Boards driven by the ESP32 8.000 MHz LEDC clock sample at **`244.140625 SPS`** (`4 MHz / 16384`), whereas boards with an 8.192 MHz clock run at exact **`250.0 SPS`**. For viewing and FFT band power, 250 Hz nominal is fine; for time-locked ERP/P300 epoching, use arrival timestamps or `eeg.getStats().measuredHz`. |

### 51-Byte Packet Layout
| Byte Offset | Content |
|---|---|
| `bytes[0]` | `0xA0` (Start marker — always validate!) |
| `bytes[1]` | `0..255` (Rolling uint8 sample counter — use to detect dropped BLE packets) |
| `bytes[2..25]` | `ADC1` Channels 1–8 (`8 × 3 bytes`, 24-bit **big-endian** signed two's complement) |
| `bytes[26..49]` | `ADC2` Channels 9–16 (`8 × 3 bytes`, 24-bit **big-endian** signed two's complement) |
| `bytes[50]` | `0xC0` (End marker — always validate!) |

### Exact 24-Bit to Microvolt (µV) Conversion
```js
const UV_SCALE = (1.2 / 4.0 / 8388607.0) * 1e6; // ~0.03576279 µV / LSB
let raw = (b0 << 16) | (b1 << 8) | b2;
if (raw >= 0x800000) raw -= 0x1000000; // 24-bit two's complement sign extension
const uV = raw * UV_SCALE;
```

---

## 3. Hexagonal Pogo-Pin Coordinates (`PiEEG.OCTOPUS_16_PINS`)

Because all 16 signal pins sit in a tight ~20 × 20 mm hexagonal array, Octopus 16 enables **high-density local spatial filtering (Surface Laplacian / Current Source Density)** and **micro-topographic heatmaps**.

| Ch | Index | ADC | `x` (mm) | `y` (mm) | | Ch | Index | ADC | `x` (mm) | `y` (mm) |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | 0 | 1 | `10.14` | `-2.72` | | **9** | 8 | 2 | `-10.14` | `2.72` |
| **2** | 1 | 1 | `7.43` | `-7.43` | | **10** | 9 | 2 | `-7.43` | `7.43` |
| **3** | 2 | 1 | `2.75` | `-4.77` | | **11** | 10 | 2 | `-2.75` | `4.76` |
| **4** | 3 | 1 | `2.72` | `-10.15` | | **12** | 11 | 2 | `-2.72` | `10.14` |
| **5** | 4 | 1 | `-2.72` | `-10.14` | | **13** | 12 | 2 | `2.72` | `10.15` |
| **6** | 5 | 1 | `-2.75` | `-4.77` | | **14** | 13 | 2 | `2.75` | `4.77` |
| **7** | 6 | 1 | `-7.42` | `-7.42` | | **15** | 14 | 2 | `7.43` | `7.42` |
| **8** | 7 | 1 | `-10.14` | `-2.73` | | **16** | 15 | 2 | `10.14` | `2.71` |

---

## 4. `pieeg.js` SDK Quick Reference

`pieeg.js` is vendored locally in `./pieeg.js` (and available via CDN at `https://cdn.jsdelivr.net/gh/pieeg-club/PiEEG-server@main/pieeg.js`). Always prefer `./pieeg.js` so hackathon apps work offline on bad Wi-Fi.

```js
const eeg = new PiEEG({
  fftSize: 256,       // Power of 2 (256 samples ≈ 1.02s window @ 250 Hz -> ~0.98 Hz resolution)
  updateHz: 15,       // FFT & band-power callback rate (Hz)
  bufferSeconds: 4,   // Per-channel ring buffer length (seconds)
  filter: {           // Browser-side DSP chain (enabled by default)
    hampel: { enabled: true, windowSize: 5, nSigma: 3.0 }, // MAD spike rejection
    bandpass: { low: 1, high: 40, order: 5 },              // 5th-order Butterworth SOS
    notch: 50,                                             // 50 Hz (EU) or 60 Hz (US/CA) or false
  },
});

// 1. Connect via Web Bluetooth (MUST be triggered inside a user click event!)
await eeg.connectBLE({ device: 'octopus-16' });

// 2. OR connect the built-in 250 Hz Simulator (no hardware needed!)
await eeg.connectSimulator({ device: 'octopus-16' });
eeg.triggerSimEvent('alpha', true); // Toggle 10 Hz Alpha eyes-closed burst
eeg.triggerSimEvent('blink');       // Inject 180 µV Fp blink spike
eeg.triggerSimEvent('clench');      // Inject high-freq jaw-clench sEMG burst

// 3. High-rate sample callback (~250 times/sec)
eeg.onData((channels, timestampSec) => {
  // channels: number[16] in µV (already Hampel + bandpass + notch filtered)
  // Optional: apply hexagonal Surface Laplacian for sharper local SNR
  const laplacian = eeg.computeLaplacian(channels);
});

// 4. Spectral callback (fires at updateHz, default 15 Hz)
eeg.onBandPowers((powers, spectrum) => {
  // powers: { Delta, Theta, Alpha, Beta, Gamma } in µV² (averaged across channels)
  // spectrum: { psd: Float64Array, freqs: Float64Array, totalPower, dominantFreq }
});

// 5. Contact quality & link health
const quality = eeg.getContactQuality(); // [{ channel, rms, status: 'good'|'railed'|'flat', pin }]
const stats = eeg.getStats();            // { connected, measuredHz, samplesReceived, packetsLost, packetLossRate }
```

---

## 5. CRITICAL Performance & Scientific Rules for AI Agents

When generating code for students in this repo, **you MUST obey these 5 rules**:

1. **NEVER Trigger UI Layout or React `setState` at 250 Hz:**
   - `eeg.onData()` runs **250 times per second** (4,000 channel values/sec).
   - **DO NOT** call `React.useState` setters, `element.innerHTML`, or `Chart.js` `.update()` inside `eeg.onData()`. It will freeze the browser tab within seconds.
   - **DO** write samples into pre-allocated `Float32Array`/`Float64Array` ring buffers (or use `eeg.channelBuffers[ch].copyLatestTo(typedArray)`), and render waveforms strictly inside a `requestAnimationFrame` loop onto a `<canvas>` or WebGL context.
   - React state updates (`useState`) are only permissible inside `eeg.onBandPowers()` (10–15 Hz) or a throttled timer (`<= 15 Hz`).

2. **Zero Allocations in the 250 Hz Hot Path:**
   - Avoid `Array.prototype.map`, `.filter`, object spreads, or `new Float32Array()` inside `onData` or `requestAnimationFrame`. Reuse typed scratch buffers.

3. **Always Include Simulator Mode (`connectSimulator`) Alongside `connectBLE`:**
   - Every app you generate MUST have both a **"Connect Octopus 16 (BLE)"** button and a **"Simulator Mode (No Hardware)"** button (plus keyboard shortcuts like `Space` for Blink, `A` for Alpha boost, `C` for Jaw Clench).
   - Why: Hackathon teams usually have 4 students sharing 1 board, and Web Bluetooth requires user gestures. Simulator mode lets everyone code and test immediately.

4. **Surface Pogo-Pin Contact Quality (`2–150 µV` RMS):**
   - Dry pogo pins must part through hair to touch the scalp. Always display a small contact-quality indicator (`eeg.getContactQuality()`) so users know if a channel is `'good'` (`2–150 µV` RMS), `'railed'` (`>150 µV`, hair blocking pin or movement), or `'flat'` (`<2 µV`).

5. **Honest Biometrics & Artifact Guardrails:**
   - Single-spot EEG over `Pz`/`Oz` is awesome for **Alpha reactivity (8–13 Hz eyes closed vs open)** and **SSVEP**.
   - Single-spot placement over the forehead (`Fp1/Fp2`) is awesome for **Eye Blinks** (large low-frequency spike `>100 µV`) and **Jaw Clenches / Forehead sEMG** (broadband high-frequency `30–100 Hz` burst).
   - **Never let an EMG jaw clench fake "High Beta Focus":** When computing `Beta / (Beta + Theta)`, gate or freeze the metric if broadband RMS (`>80 µV`) or `Gamma` power spikes suddenly (muscle artifact).
