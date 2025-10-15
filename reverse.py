#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import time
import requests
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# --- Konfiguration ---
NOMINATIM_URL = "http://localhost:8088/reverse"
DELAY = 0.05  # 50ms zwischen Requests
MAX_THREADS = 16
DB_USER = "VMadmin"
DB_PASS = "Qwdg2302"
HOST = "localhost"

csv_lock = Lock()
cache = {}

def start_nominatim_server(db_name):
    """Startet Nominatim-Server mit passender DB"""
    # libpq-Format: dbname=... user=... password=... host=...
    dsn = f"dbname={db_name} user={DB_USER} password={DB_PASS} host={HOST}"
    print(f"Starte Nominatim-Server für DB '{db_name}' ...")

    process = subprocess.Popen(
        [
            "python3",
            "/home/VMadmin/nominatim/nominatim-source/nominatim-cli.py",
            "serve"
        ],
        env={**os.environ, "NOMINATIM_DATABASE_DSN": dsn},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Warten, bis Server erreichbar ist
    for i in range(30):
        try:
            r = requests.get("http://localhost:8088/status", timeout=1)
            if r.status_code == 200:
                print("✅ Nominatim-Server läuft.")
                return process
        except:
            pass
        time.sleep(1)

    print("⚠️  Serverstart fehlgeschlagen.")
    process.terminate()
    return None



def stop_nominatim_server(process):
    """Beendet den Nominatim-Server-Prozess"""
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("🛑 Nominatim-Server gestoppt.\n")

def reverse_geocode(node):
    lat = float(node["lat"])
    lon = float(node["lon"])
    place_id = node.get("place_id", "")
    key = (lat, lon)

    if key in cache:
        return place_id, lat, lon, *cache[key]

    params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
    try:
        resp = requests.get(NOMINATIM_URL, params=params, timeout=10)
        data = resp.json()
        address = data.get("address", {})
        road = address.get("road", "")
        postcode = address.get("postcode", "")
        city = address.get("city", "") or address.get("town", "") or address.get("village", "")
        cache[key] = (road, postcode, city)
    except Exception as e:
        print(f"Fehler bei Node {place_id}: {e}")
        road = postcode = city = ""

    time.sleep(DELAY)
    return place_id, lat, lon, road, postcode, city

def process_csv(input_file):
    suffix = input_file.split("_")[-1].split(".")[0]
    db_name = f"data{suffix}"
    output_file = f"completeList_{suffix}.csv"

    print(f"\n=== Verarbeite {input_file} auf DB {db_name} ===")

    # Server starten
    process = start_nominatim_server(db_name)
    if not process:
        print(f"❌ Konnte Nominatim-Server für {db_name} nicht starten.")
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f_out:
        fieldnames = ["place_id", "lat", "lon", "road", "postcode", "city"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        with open(input_file, newline="", encoding="utf-8") as f_in:
            reader = csv.DictReader(f_in)
            nodes = list(reader)

        print(f"{len(nodes)} Nodes geladen, Verarbeitung mit {MAX_THREADS} Threads...")

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_node = {executor.submit(reverse_geocode, node): node for node in nodes}
            processed = 0

            for future in as_completed(future_to_node):
                place_id, lat, lon, road, postcode, city = future.result()
                with csv_lock:
                    writer.writerow({
                        "place_id": place_id,
                        "lat": lat,
                        "lon": lon,
                        "road": road,
                        "postcode": postcode,
                        "city": city
                    })
                processed += 1
                if processed % 1000 == 0:
                    print(f">>> {processed} Nodes verarbeitet...")

    stop_nominatim_server(process)
    print(f"=== Verarbeitung von {input_file} abgeschlossen. Ergebnisse gespeichert in '{output_file}' ===")

if __name__ == "__main__":
    csv_files = sorted(glob.glob("allNodesRounded_*.csv"))
    if not csv_files:
        print("Keine passenden CSV-Dateien gefunden.")
        exit(1)

    for csv_file in csv_files:
        process_csv(csv_file)

    print("\nAlle Aufgaben abgeschlossen.")
