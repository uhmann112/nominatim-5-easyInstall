import subprocess
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Maximum number of simultaneous threads
MAX_WORKERS = 2 # adjust depending on CPU/SSD

# File with download links
infoFile = "info.txt"

# List for downloaded PBF files
links = []

# Download the PBF files
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
            print(f"Error downloading PBF file (Exit code {wget_result.returncode}).")
            exit(1)
        else:
            print(f"Download of {outputFile} completed successfully.\n")
            time.sleep(1)

        links.append(outputFile)
        fileSuffix += 1

# Scripts to run after import for each file
scripts = [
    "searchAllNodes.py",
    "round.py"
]

# Project directory (where nominatim-cli.py is located)
project_dir = os.path.expanduser("~/nominatim/nominatim-project")
nominatim_cli_path = os.path.expanduser("~/nominatim/nominatim-source/nominatim-cli.py")

def run_nominatim_import(pbf_file):
    dbName = os.path.splitext(pbf_file)[0]  # e.g., data1 -> DB name
    print(f"Starting Nominatim import for {pbf_file} on DB {dbName} ...")

    env = os.environ.copy()
    env["NOMINATIM_DATABASE_DSN"] = f"pgsql:dbname={dbName}"
    env["NOMINATIM_DATA_DIR"] = f"/mnt/ssd/{dbName}"  # optional: separate data dirs

    result = subprocess.run([
        "python3", nominatim_cli_path,
        "import",
        "--osm-file", os.path.abspath(pbf_file),
        "--project-dir", project_dir,
        "--threads", "8"
    ], cwd=os.path.dirname(nominatim_cli_path), env=env)

    if result.returncode != 0:
        print(f"Error importing {pbf_file} (Exit code {result.returncode})")
        return False, dbName

    print(f"Import for {pbf_file} completed successfully.")
    return True, dbName

def run_script(script, dbName, suffix):
    print(f"Starting {script} for DB {dbName} with suffix {suffix} ...")

    result = subprocess.run([
        "python3",
        script,
        dbName,        # Argument 1: database name
        str(suffix)    # Argument 2: suffix for input/output files
    ])

    if result.returncode != 0:
        print(f"{script} for DB {dbName} failed (Exit code {result.returncode})")
        return False

    print(f"{script} for DB {dbName} completed successfully.")
    return True

# Parallel execution of imports
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    import_futures = {executor.submit(run_nominatim_import, pbf): pbf for pbf in links}

    # Wait until all imports are completed
    successful_dbs = []
    for future in as_completed(import_futures):
        success, dbName = future.result()
        if success:
            successful_dbs.append(dbName)

# Post-processing per DB (serial)
for suffix, dbName in enumerate(successful_dbs, start=1):
    for script in scripts:
        run_script(script, dbName, suffix)

print("All tasks completed.")
