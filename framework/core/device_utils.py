"""Helpers for finding the Android phone connected over USB via adb."""

import os
import shutil
import subprocess
from pathlib import Path


def find_adb():
    adb = shutil.which("adb")
    if adb:
        return adb
    sdk = android_sdk_root()
    if sdk:
        candidate = Path(sdk) / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
        if candidate.exists():
            return str(candidate)
    return None


def android_sdk_root():
    """ANDROID_HOME / ANDROID_SDK_ROOT, else the default Android Studio location, else derived from adb on PATH."""
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(var) and Path(os.environ[var]).exists():
            return os.environ[var]
    default = Path(os.environ.get("LOCALAPPDATA", "")) / "Android" / "Sdk"
    if default.exists():
        return str(default)
    adb = shutil.which("adb")
    if adb:
        return str(Path(adb).resolve().parent.parent)
    return None


def connected_devices():
    """Serials of devices in the 'device' state (excludes unauthorized/offline)."""
    adb = find_adb()
    if not adb:
        return []
    out = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=30).stdout
    serials = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def android_version(serial):
    adb = find_adb()
    out = subprocess.run(
        [adb, "-s", serial, "shell", "getprop", "ro.build.version.release"],
        capture_output=True, text=True, timeout=30,
    ).stdout
    return out.strip() or None


def device_model(serial):
    adb = find_adb()
    out = subprocess.run(
        [adb, "-s", serial, "shell", "getprop", "ro.product.model"],
        capture_output=True, text=True, timeout=30,
    ).stdout
    return out.strip() or None
