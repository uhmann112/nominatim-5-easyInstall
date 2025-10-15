#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import psycopg
import sys

# Read arguments
dbName = sys.argv[1]      # e.g., "data1"
suffix = sys.argv[2]      # e.g., "1"

# =====================
# CONFIGURATION
# =====================
DB_NAME = dbName
DB_USER = os.getenv("DB_USER", "VMadmin")
DB_PASS = os.getenv("DB_PASS", "Qwdg2302")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
OUTPUT_FILE = f"allNodes_{suffix}.csv"

print(f"searchAllnodes started, scanning DB: {DB_NAME}")

# =====================
# SQL QUERY: ALL NODES WITH COORDINATES
# =====================
query = """
SELECT
    place_id,
    ST_Y(centroid) AS lat,
    ST_X(centroid) AS lon
FROM placex
WHERE centroid IS NOT NULL;
"""

# =====================
# DB CONNECTION AND DATA LOADING
# =====================
try:
    with psycopg.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            print(f"Connected to DB '{DB_NAME}' successfully.")
            cur.execute(query)
            rows = cur.fetchall()
            print(f"{len(rows)} nodes loaded.")
except Exception as e:
    print("Error connecting to DB:", e)
    exit(1)

# =====================
# WRITE CSV
# =====================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["place_id", "lat", "lon"])
    writer.writerows(rows)

print(f"All nodes have been saved in '{OUTPUT_FILE}'.")
