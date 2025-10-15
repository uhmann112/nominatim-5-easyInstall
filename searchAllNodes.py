#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import psycopg
import sys

# Argumente auslesen
dbName = sys.argv[1]      # z.B. "data1"
suffix = sys.argv[2]      # z.B. "1"
# =====================
# KONFIGURATION
# =====================
DB_NAME = dbName
DB_USER = os.getenv("DB_USER", "VMadmin")
DB_PASS = os.getenv("DB_PASS", "Qwdg2302")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
suffix = suffix
OUTPUT_FILE = f"allNodes_{suffix}.csv"

print(f"searchAllnodes startet mit durchsuchen von db: {DB_NAME}")

# =====================
# SQL QUERY: ALLE NODES MIT COORDINATEN
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
# DB VERBINDUNG UND DATEN LADEN
# =====================
try:
    with psycopg.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        host=DB_HOST, port=DB_PORT
    ) as conn:
        with conn.cursor() as cur:
            print(f" Verbunden mit DB '{DB_NAME}' erfolgreich.")
            cur.execute(query)
            rows = cur.fetchall()
            print(f" {len(rows)} Nodes geladen.")
except Exception as e:
    print(" Fehler bei der Verbindung:", e)
    exit(1)

# =====================
# CSV SCHREIBEN
# =====================
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["place_id", "lat", "lon"])
    writer.writerows(rows)

print(f" Alle Nodes wurden in '{OUTPUT_FILE}' gespeichert.")
