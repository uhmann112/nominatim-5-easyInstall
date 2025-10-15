#!/usr/bin/env bash
set -e
set -o pipefail

# --- Configuration ---
NOMINATIM_USER="VMadmin"
NOMINATIM_DIR="/home/${NOMINATIM_USER}/nominatim"
PROJECT_DIR="${NOMINATIM_DIR}/nominatim-project"
PG_USER="nominatim"
PG_DB="nominatim"
PG_VERSION="15"
THREADS=8

# --- System Update ---
sudo apt update
sudo apt upgrade -y

# --- Install dependencies ---
sudo apt install -y \
  build-essential cmake g++ libboost-all-dev \
  libexpat1-dev zlib1g-dev libxml2-dev libpq-dev libbz2-dev libproj-dev \
  postgresql postgresql-contrib postgis postgresql-postgis-scripts \
  python3 python3-pip python3-psycopg2 python3-setuptools python3-dev \
  git wget curl

# --- Remove old installation ---
sudo systemctl stop nominatim || true
sudo systemctl disable nominatim || true
sudo rm -rf ${NOMINATIM_DIR}

sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${PG_DB};" || true
sudo -u postgres psql -c "DROP ROLE IF EXISTS ${PG_USER};" || true

# --- Create directories ---
cd ~
rm -rf ~/nominatim
mkdir ~/nominatim
cd ~/nominatim
mkdir nominatim-project
git clone --recursive https://github.com/openstreetmap/Nominatim.git nominatim-source
cd nominatim-source

# --- Clone Nominatim ---
git checkout $(git tag | grep -v rc | tail -1)

# --- Setup Python virtual environment ---
python3 -m venv nominatim-venv
cd ~/nominatim/nominatim-source
source nominatim-venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install "uvicorn[standard]"
pip install psycopg[binary] uvicorn[standard] SQLAlchemy click Jinja2 falcon psutil  PyICU requests


cd ~/nominatim/nominatim-source/data
wget https://nominatim.org/data/country_grid.sql.gz -O country_osm_grid.sql.gz

# --- Setup PostgreSQL user and database ---
sudo -u postgres createuser -s ${PG_USER} || true
sudo -u postgres createdb -E UTF8 -O ${PG_USER} ${PG_DB} || true
sudo -u postgres psql -d ${PG_DB} -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d ${PG_DB} -c "CREATE EXTENSION IF NOT EXISTS hstore;"


# Als postgres-Benutzer psql starten und die User erstellen
sudo -u postgres psql <<EOSQL



CREATE USER "www-data" WITH PASSWORD 'Qwdg2302';
EOSQL

echo "Benutzer 'nominatim' und 'www-data' wurden erstellt."


export NOMINATIM_DATABASE_DSN="pgsql:dbname=${PG_DB} user=\"VMadmin\" password=Qwdg2302 host=localhost"


# --- Done ---
echo "Nominatim installation scaffold created at ${NOMINATIM_DIR}."
echo "Next steps:"
echo "1. copy osm-data links into nominatim-project/info.txt"
echo "2. Start venv with nvenv and start master script with python3 MASTER.py "
echo "3. start the reverse geocoding with python3 reverse.py"

echo "nvenv  and nserve"
echo "python3 /home/VMadmin/nominatim/nominatim-source/nominatim-cli.py serve"

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='VMadmin'" | grep -q 1 || sudo -u postgres createuser VMadmin --superuser

sudo -u postgres psql -c "ALTER USER VMadmin WITH PASSWORD 'Qwdg2302';"

echo "alias nvenv='source ~/nominatim/nominatim-source/nominatim-venv/bin/activate'" >> ~/.bashrc
source ~/.bashrc

echo "alias nserve='python3 /home/VMadmin/nominatim/nominatim-source/nominatim-cli.py serve'" >> ~/.bashrc
source ~/.bashrc
