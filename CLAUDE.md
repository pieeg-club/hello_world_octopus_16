# CLAUDE.md — Claude Code Instructions for Octopus 16 Hackathon Starter

Please read and follow all hardware specifications, BLE protocol details, `pieeg.js` SDK methods, and real-time performance rules in **[AGENTS.md](./AGENTS.md)** and **[PROMPTS.md](./PROMPTS.md)**.

## Quick Checklist Before Writing Code
1. **Use `./pieeg.js`** — already present in the project root with Web Bluetooth (`device: 'octopus-16'`) + 250 Hz Simulator (`connectSimulator()`) + 16-pin hexagonal spatial helpers (`PiEEG.OCTOPUS_16_PINS`, `getContactQuality()`, `computeLaplacian()`).
2. **Decouple 250 Hz acquisition from 60 fps rendering** — never trigger DOM updates or React re-renders inside `eeg.onData()`. Render waveforms in `requestAnimationFrame` using `<canvas>`.
3. **Always provide both `Connect Octopus 16 (BLE)` and `250 Hz Simulator` buttons** so hackathon teammates without the physical board can test every feature immediately.
4. **Gate BCI metrics against artifacts** — check `eeg.getContactQuality()` (`2–150 µV` RMS) and prevent eye blinks (`>110 µV` peak) or jaw clenches (high `Gamma` / broadband RMS) from falsely triggering cognitive band-power ratios.
