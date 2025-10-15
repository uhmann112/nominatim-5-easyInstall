import subprocess
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Maximale Anzahl gleichzeitig laufender Threads
MAX_WORKERS = 3 # anpassen je nach CPU/SSD

# Datei mit Download-Links
infoFile = "info.txt"

# Liste für heruntergeladene PBF-Dateien
links = []

# Download der PBF-Dateien
fileSuffix = 1
with open(infoFile, "r", encoding="utf-8") as f:
    for line in f:
        downloadLink = line.strip()
        outputFile = f"data{fileSuffix}.pbf"

        wget_result = subprocess.run([
            "wget",
            downloadLink,
            "-O", outputFile,
        ])
        if wget_result.returncode != 0:
            print(f"Fehler beim Herunterladen der PBF-Datei (Exit-Code {wget_result.returncode}).")
            exit(1)
        else:
            print(f"Download von {outputFile} erfolgreich abgeschlossen.\n")
            time.sleep(1)

        links.append(outputFile)
        fileSuffix += 1

# Scripts, die nach dem Import für jede Datei ausgeführt werden
scripts = [
    "searchAllNodes.py",
    "round.py"
]

# Projektverzeichnis (wo nominatim-cli.py liegt)
project_dir = os.path.expanduser("~/nominatim/nominatim-project")
nominatim_cli_path = os.path.expanduser("~/nominatim/nominatim-source/nominatim-cli.py")
def run_nominatim_import(pbf_file):
    dbName = os.path.splitext(pbf_file)[0]  # z.B. data1 -> data1 als DB-Name
    print(f"Starte Nominatim Import für {pbf_file} auf DB {dbName} ...")

    env = os.environ.copy()
    env["NOMINATIM_DATABASE_DSN"] = f"pgsql:dbname={dbName}"
    env["NOMINATIM_DATA_DIR"] = f"/mnt/ssd/{dbName}"  # optional: verschiedene Data-Dirs

    result = subprocess.run([
        "python3", nominatim_cli_path,
        "import",
        "--osm-file", os.path.abspath(pbf_file),
        "--project-dir", project_dir,
        "--threads", "8"
    ], cwd=os.path.dirname(nominatim_cli_path), env=env)

    if result.returncode != 0:
        print(f"Fehler beim Import {pbf_file} (Exit-Code {result.returncode})")
        return False, dbName

    print(f"Import für {pbf_file} erfolgreich abgeschlossen.")
    return True, dbName

def run_script(script, dbName, suffix):
    print(f"Starte {script} für DB {dbName} mit Suffix {suffix} ...")

    result = subprocess.run([
        "python3",
        script,
        dbName,        # Argument 1: Name der Datenbank
        str(suffix)    # Argument 2: Suffix für Input/Output-Dateien
    ])

    if result.returncode != 0:
        print(f"{script} für DB {dbName} hat einen Fehler verursacht (Exit-Code {result.returncode})")
        return False

    print(f"{script} für DB {dbName} erfolgreich abgeschlossen.")
    return True

# Parallele Ausführung der Imports
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    import_futures = {executor.submit(run_nominatim_import, pbf): pbf for pbf in links}

    # Warten bis alle Imports abgeschlossen sind
    successful_dbs = []
    for future in as_completed(import_futures):
        success, dbName = future.result()
        if success:
            successful_dbs.append(dbName)

# Nachbearbeitung pro DB seriell
for suffix, dbName in enumerate(successful_dbs, start=1):
    for script in scripts:
        run_script(script, dbName, suffix)

print("Alle Aufgaben abgeschlossen.")
