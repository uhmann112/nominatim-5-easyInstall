#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys

# =====================
# READ ARGUMENTS
# =====================
suffix = sys.argv[2]  # e.g., "1"

# =====================
# INPUT/OUTPUT
# =====================
INPUT_FILE = f"allNodes_{suffix}.csv"
OUTPUT_FILE = f"allNodesRounded_{suffix}.csv"
# Rounding: approx. 50 m
ROUND_DECIMALS = 3  # 3 decimal places ≈ 50-100 m

# =====================
# PROCESS NODES
# =====================
unique_nodes = {}

with open(INPUT_FILE, newline="", encoding="utf-8") as f_in:
    reader = csv.DictReader(f_in)
    for row in reader:
        lat = round(float(row["lat"]), ROUND_DECIMALS)
        lon = round(float(row["lon"]), ROUND_DECIMALS)
        key = (lat, lon)

        # Only store one node per rounded key
        if key not in unique_nodes:
            unique_nodes[key] = {
                "place_id": row.get("place_id", ""),
                "lat": lat,
                "lon": lon
            }

print(f"{len(unique_nodes)} unique coordinates after rounding to {ROUND_DECIMALS} decimals.")

# =====================
# WRITE CSV
# =====================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f_out:
    fieldnames = ["place_id", "lat", "lon"]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    for node in unique_nodes.values():
        writer.writerow(node)

print(f"Rounded and merged nodes saved in '{OUTPUT_FILE}'")
