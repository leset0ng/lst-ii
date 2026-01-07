#!/usr/bin/env python3
import glob
import os
import sys


def get_content(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except:
        return ""


def find_best_temp_input(hwmon_path):
    """
    Finds the best temperature input file in a hwmon directory.
    Prioritizes labeled inputs (Package, Tdie, Edge).
    """
    candidates = {}  # path -> score

    # Get all temp inputs
    input_files = glob.glob(os.path.join(hwmon_path, "temp*_input"))

    if not input_files:
        return None

    for input_path in input_files:
        base = input_path.replace("_input", "")
        label_path = base + "_label"
        label = get_content(label_path).lower()

        score = 1  # Default score for existing input

        # Prioritize based on label
        if "package" in label:
            score = 20
        elif "tdie" in label:
            score = 20
        elif "tctl" in label:
            score = 15  # Tctl is often offset, but better than random
        elif "edge" in label:
            score = 15  # GPU edge is standard
        elif "junction" in label:
            score = 10
        elif "composite" in label:
            score = 10
        elif "core" in label:
            score = 5  # Specific cores are less useful than package

        # Sanity check: ensure the file is readable and has a valid value
        try:
            val_str = get_content(input_path)
            if not val_str:
                continue
            val = int(val_str)
            if val <= 0:
                continue  # Ignore 0 or negative
        except:
            continue

        candidates[input_path] = score

    if not candidates:
        return None

    # Return the path with the highest score
    best_path = None
    best_score = -1
    for path, score in candidates.items():
        if score > best_score:
            best_score = score
            best_path = path

    return best_path


def detect():
    cpu_path = None
    gpu_path = None

    # 1. Scan HWMON (Preferred)
    # Sort to ensure consistent order, though we check all
    hwmon_dirs = sorted(glob.glob("/sys/class/hwmon/hwmon*"))

    for hwmon in hwmon_dirs:
        name = get_content(os.path.join(hwmon, "name"))
        best_input = find_best_temp_input(hwmon)

        if not best_input:
            continue

        # CPU Detection
        # k10temp/zenpower: AMD
        # coretemp: Intel
        # cpu_thermal: RPi/ARM
        # fam15h_power: Old AMD
        if name in [
            "coretemp",
            "k10temp",
            "zenpower",
            "cpu_thermal",
            "fam15h_power",
            "asus_ec",
        ]:
            # If we already found a CPU path, only replace it if the new one is "better" (e.g. Package vs Core)
            # But simpler logic: first "Package" or "Tdie" wins.
            if not cpu_path:
                cpu_path = best_input
            elif (
                "package" in get_content(best_input.replace("_input", "_label")).lower()
            ):
                cpu_path = best_input  # Upgrade to package if we had something else

        # GPU Detection
        if name in ["amdgpu", "radeon", "nouveau", "nvidia", "i915"]:
            if not gpu_path:
                gpu_path = best_input

    # 2. Fallback to Thermal Zones (if missing)
    if not cpu_path or not gpu_path:
        for tz in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
            tz_type = get_content(os.path.join(tz, "type")).lower()
            temp_path = os.path.join(tz, "temp")

            if not os.path.exists(temp_path):
                continue

            # Avoid redundant checks if we already have paths
            if not cpu_path and any(x in tz_type for x in ["cpu", "x86_pkg_temp"]):
                cpu_path = temp_path

            if not gpu_path and any(x in tz_type for x in ["gpu"]):
                gpu_path = temp_path

    # Output results compatible with QML SplitParser
    # Resolve symlinks for FileView compatibility
    if cpu_path:
        print(f"cpu:{os.path.realpath(cpu_path)}")
    if gpu_path:
        print(f"gpu:{os.path.realpath(gpu_path)}")


if __name__ == "__main__":
    detect()
