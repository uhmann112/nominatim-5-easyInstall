# <p align="center">Nominatim Automation Scripts</p>

This repository contains a set of scripts designed to simplify the setup and use of Nominatim for geocoding.
It supports importing multiple OpenStreetMap (OSM) datasets in parallel, running reverse geocoding queries concurrently, and generating full address lists.

## Features

Automated installation of system dependencies and Python environment.

Parallel import of multiple OSM datasets into separate PostgreSQL databases.

Parallel reverse geocoding of coordinates to generate complete address lists.

Fully configurable thread counts to match system specifications.

Easy-to-use scripts with minimal manual setup.

## steps:

Prepare the environment

you have to have installed:
-pip3
-python3
-PyICU
-osm2pgsql

also install dos2unix to ensure the install script works properly:
```bash
sudo apt install dos2unix
dos2unix install.sh
```
Make the install script executable:
```bash
chmod +x install.sh
```
Run the installation script

Execute:
```bash
./install.sh
```

## The script will:

Install all required system dependencies (PostgreSQL, PostGIS, build tools, Python development packages).

Create a Python virtual environment in nominatim/nominatim-venv.

Install all necessary Python packages for the scripts and Nominatim.

Set up project directories.

Project Structure

After installation, the directory nominatim/nominatim-project will be created. there you put the main scripts:

MASTER.py – orchestrates parallel processing and reverse geocoding.

info.txt – contains dataset download links.

searchAllNode.py – handles node-based searches.

round.py – rounds coordinates if necessary.

reverse.py – performs reverse geocoding using Nominatim.

The virtual environment is located at nominatim/nominatim-venv.

## Configuration

Parallel Threads:
The number of threads can be adjusted depending on system specifications.
Change the variable MAX_THREADS in MASTER.py to configure parallel execution.

Database User:
Scripts expect the user VMadmin by default. If your username differs, update it in the scripts accordingly.


Activate the virtual environment:

the install.sh script will have created shortcuts for running the server and starting the venv.
just enable them with :
```bash
source /home/VMadmin/.bashrc
```




type nvenv to start the virtual environment

to test if the servers are running type nserve  and then exit with ctlr + C to stop.

if the shortcuts don´t  work run following comands in the shell:

```Bash
echo "alias nvenv='source /home/VMadmin/nominatim/nominatim-source/nominatim-venv/bin/activate'" >> /home/VMadmin/.bashrc
echo "alias nserve='python3 /home/VMadmin/nominatim/nominatim-source/nominatim-cli.py serve'" >> /home/VMadmin/.bashrc
```



## Workflow

Import datasets
put your osm downloadlinks in info.txt (1 link per row, no empty rows!!!), then run the MASTER.py script:
```bash
python3 MASTER.py
```
This step creates all necessary tables, including import_status, placex, and others required for geocoding.

Run reverse geocoding
After datasets are imported, reverse.py  can be run to generate full address lists.
```bash
python3 reverse.py
```
The output CSV files include:

Coordinates (lat, lon)

Street names

Postal codes



City names

Post-processing
After all CSV files are generated, PostgreSQL databases can be deleted if you want to start a fresh import.

Notes
if something with the servers doesn´t seem right:   
Make sure the Nominatim server is not running multiple instances on the same port, or the scripts will fail to start.


## Primary Use Case

This setup is ideal for generating a complete address database from multiple OSM datasets.
It is designed to:

Handle multiple datasets efficiently with parallel processing.

Produce a comprehensive list of coordinates, street names, cities, and postal codes for further analysis or applications.


# have fun!!