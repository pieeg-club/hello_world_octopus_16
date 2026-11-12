#!/usr/bin/env python3
"""
Octopus 16 — 60-Second Python Quickstart (BLE + Simulator + CSV + Optional LSL)

Streams 16 channels @ 250 Hz from an Octopus 16 board over Bluetooth Low Energy
using `bleak`, decodes the 51-byte ADS131M08 packets into microvolts (µV),
tracks packet loss via the rolling 0..255 counter, checks pogo-pin scalp contact
quality (RMS µV), and optionally logs to CSV or broadcasts to LabStreamingLayer (LSL).

Install:
    pip install bleak numpy

Usage:
    python python_quickstart.py                  # Auto-discover Octopus 16 via BLE
    python python_quickstart.py --sim            # Run 250 Hz synthetic simulator (no hardware)
    python python_quickstart.py --csv out.csv    # Record 16-ch µV stream to CSV
    python python_quickstart.py --lsl            # Broadcast 16-ch stream to LSL (requires pylsl)
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import math
import random
import sys
import time
from collections import deque
from typing import Deque, List, Optional

import numpy as np

# ── Verified Octopus 16 BLE Protocol Constants ──────────────────────────────
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
NOTIFY_CHAR_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
CMD_CHAR_UUID = "c0de0001-36e1-4688-b7f5-ea07361b26a8"

PACKET_SIZE = 51
START_MARKER = 0xA0
END_MARKER = 0xC0
NUM_CHANNELS = 16
NOMINAL_SPS = 250

# ADS131M08: Vref = 1.2 V, PGA Gain = 4.0, Full-scale = 2^23 - 1 = 8388607
UV_SCALE = (1.2 / 4.0 / 8388607.0) * 1_000_000.0  # ~0.03576279 µV / LSB


def decode_octopus16_packet(packet: bytes | bytearray) -> Optional[tuple[int, list[float]]]:
    """Decode a single 51-byte Octopus 16 BLE notification into (counter, 16-ch µV list)."""
    if len(packet) < PACKET_SIZE:
        return None
    if packet[0] != START_MARKER or packet[PACKET_SIZE - 1] != END_MARKER:
        return None

    counter = packet[1]
    channels: list[float] = []
    for ch in range(NUM_CHANNELS):
        off = 2 + ch * 3
        raw = (packet[off] << 16) | (packet[off + 1] << 8) | packet[off + 2]
        if raw & 0x800000:
            raw -= 1 << 24
        channels.append(round(raw * UV_SCALE, 2))
    return counter, channels


class StreamMonitor:
    """Tracks SPS, dropped BLE packets, per-channel RMS contact quality, and Alpha/Beta power."""

    def __init__(self, csv_path: Optional[str] = None, use_lsl: bool = False) -> None:
        self.buffers: List[Deque[float]] = [deque(maxlen=256) for _ in range(NUM_CHANNELS)]
        self.samples_received = 0
        self.packets_lost = 0
        self.last_counter: Optional[int] = None
        self.t_start = time.perf_counter()
        self.last_print = time.perf_counter()

        self.csv_file = open(csv_path, "w", newline="", encoding="utf-8") if csv_path else None
        self.csv_writer = csv.writer(self.csv_file) if self.csv_file else None
        if self.csv_writer:
            self.csv_writer.writerow(
                ["timestamp_s", "counter"] + [f"CH{i+1}_uV" for i in range(NUM_CHANNELS)]
            )

        self.lsl_outlet = None
        if use_lsl:
            from pylsl import StreamInfo, StreamOutlet  # type: ignore

            info = StreamInfo("Octopus16", "EEG", NUM_CHANNELS, NOMINAL_SPS, "float32", "octopus16_ble")
            self.lsl_outlet = StreamOutlet(info)
            print("[LSL] Broadcasting 16-channel EEG stream as 'Octopus16'")

    def ingest(self, counter: int, channels: list[float]) -> None:
        now = time.time()
        if self.last_counter is not None:
            expected = (self.last_counter + 1) & 0xFF
            if counter != expected:
                gap = (counter - expected + 256) & 0xFF
                if gap < 128:
                    self.packets_lost += gap
        self.last_counter = counter
        self.samples_received += 1

        for ch in range(NUM_CHANNELS):
            self.buffers[ch].append(channels[ch])

        if self.csv_writer:
            self.csv_writer.writerow([f"{now:.4f}", counter] + channels)

        if self.lsl_outlet:
            self.lsl_outlet.push_sample(channels)

        perf_now = time.perf_counter()
        if perf_now - self.last_print >= 1.0:
            self.last_print = perf_now
            self.print_hud()

    def print_hud(self) -> None:
        elapsed = max(1e-3, time.perf_counter() - self.t_start)
        sps = self.samples_received / elapsed
        if len(self.buffers[0]) < 256:
            print(f"[Octopus 16] Buffering... {len(self.buffers[0])}/256 samples ({sps:.1f} SPS)")
            return

        arr = np.array(self.buffers, dtype=np.float64)  # shape: (16, 256)
        arr_zero = arr - np.mean(arr, axis=1, keepdims=True)
        rms_per_ch = np.sqrt(np.mean(arr_zero[:, -125:] ** 2, axis=1))
        good_pins = int(np.sum((rms_per_ch >= 2.0) & (rms_per_ch <= 150.0)))

        # Hanning FFT across all 16 channels
        win = np.hanning(256)
        win_norm = 2.0 / (NOMINAL_SPS * np.sum(win**2))
        spec = np.fft.rfft(arr_zero * win, axis=1)
        psd = (np.abs(spec) ** 2) * win_norm
        freqs = np.fft.rfftfreq(256, d=1.0 / NOMINAL_SPS)
        df = freqs[1] - freqs[0]

        mean_psd = np.mean(psd, axis=0)
        alpha = float(np.sum(mean_psd[(freqs >= 8.0) & (freqs < 13.0)]) * df)
        beta = float(np.sum(mean_psd[(freqs >= 13.0) & (freqs < 30.0)]) * df)
        theta = float(np.sum(mean_psd[(freqs >= 4.0) & (freqs < 8.0)]) * df)
        relax = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5

        print(
            f"[Octopus 16] {sps:5.1f} SPS | Samples: {self.samples_received:6d} (Lost: {self.packets_lost}) | "
            f"Good Pins: {good_pins:2d}/16 | Alpha: {alpha:6.1f} uV^2 | Beta: {beta:5.1f} uV^2 | "
            f"Theta: {theta:5.1f} uV^2 | Relax a/(a+b): {relax:.2f}"
        )

    def close(self) -> None:
        if self.csv_file:
            self.csv_file.close()


async def run_simulator(monitor: StreamMonitor) -> None:
    print("[Simulator] Starting 250 Hz 16-channel Octopus 16 synthetic stream (Ctrl+C to stop)...")
    counter = 0
    sample_idx = 0
    dt = 1.0 / NOMINAL_SPS
    next_t = time.perf_counter()

    while True:
        now = time.perf_counter()
        while now >= next_t:
            t = sample_idx * dt
            sample_idx += 1
            next_t += dt

            # Alternate every 6 seconds between baseline and strong 10 Hz Eyes-Closed Alpha burst
            alpha_amp = 32.0 if (int(t) // 6) % 2 == 1 else 6.0
            base = (
                6.0 * math.sin(2 * math.pi * 2.5 * t)
                + 5.0 * math.sin(2 * math.pi * 6.0 * t)
                + alpha_amp * math.sin(2 * math.pi * 10.2 * t)
                + 6.0 * math.sin(2 * math.pi * 20.0 * t)
            )
            channels = [round(base * (0.9 + 0.015 * ch) + random.uniform(-4.0, 4.0), 2) for ch in range(NUM_CHANNELS)]
            monitor.ingest(counter, channels)
            counter = (counter + 1) & 0xFF

        await asyncio.sleep(0.002)


async def run_ble(monitor: StreamMonitor) -> None:
    from bleak import BleakClient, BleakScanner  # type: ignore

    print(f"[BLE] Scanning for Octopus 16 (Service UUID {SERVICE_UUID})...")

    def match_octopus(device, adv) -> bool:
        uuids = [u.lower() for u in (adv.service_uuids or [])]
        if SERVICE_UUID in uuids:
            return True
        name = (device.name or adv.local_name or "").lower()
        return name.startswith(("octopus", "octopos", "bioron", "pieeg"))

    device = await BleakScanner.find_device_by_filter(match_octopus, timeout=10.0)
    if not device:
        print(
            "[BLE] No Octopus 16 found. Ensure the board is powered via a 5 V power bank "
            "(slow 1 Hz LED blink) or run with `--sim` for the 250 Hz simulator."
        )
        sys.exit(1)

    print(f"[BLE] Connecting to {device.name or device.address}...")
    async with BleakClient(device) as client:
        print(f"[BLE] Connected! Subscribing to {NOTIFY_CHAR_UUID}...")

        def on_notify(_sender: int, data: bytearray) -> None:
            for offset in range(0, len(data) - PACKET_SIZE + 1, PACKET_SIZE):
                decoded = decode_octopus16_packet(data[offset : offset + PACKET_SIZE])
                if decoded:
                    monitor.ingest(decoded[0], decoded[1])

        await client.start_notify(NOTIFY_CHAR_UUID, on_notify)
        print("[BLE] Streaming 16 channels @ 250 Hz (Ctrl+C to stop)...")
        while client.is_connected:
            await asyncio.sleep(0.5)


def main() -> None:
    parser = argparse.ArgumentParser(description="Octopus 16 Python Quickstart")
    parser.add_argument("--sim", action="store_true", help="Run 250 Hz synthetic simulator (no hardware required)")
    parser.add_argument("--csv", type=str, default=None, help="Save 16-channel stream to CSV file")
    parser.add_argument("--lsl", action="store_true", help="Broadcast stream to LabStreamingLayer (pylsl)")
    args = parser.parse_args()

    monitor = StreamMonitor(csv_path=args.csv, use_lsl=args.lsl)
    try:
        if args.sim:
            asyncio.run(run_simulator(monitor))
        else:
            asyncio.run(run_ble(monitor))
    except KeyboardInterrupt:
        print("\n[Octopus 16] Stopped cleanly.")
    finally:
        monitor.close()


if __name__ == "__main__":
    main()
