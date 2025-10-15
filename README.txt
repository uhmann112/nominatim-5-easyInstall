To make the install.sh script executable, first install dos2unix with
"sudo apt install dos2unix". Then make the script executable with
"chmod +x install.sh".

The script can then be run with "./install.sh".

IMPORTANT:
The scripts expect the user to be VMadmin. If this is not your username,
you can easily change it directly in the scripts.

During installation, a directory called nominatim-project will be created
inside the nominatim folder. All scripts go into this directory, including
MASTER.py, info.txt, searchAllNode.py, round.py, and reverse.py.

The number of parallel threads can be adjusted according to your system.
To do this, change the variable "MAX_THREADS" in MASTER.py.

After completing all steps, CSV files will be generated containing all
street names, postal codes, and cities from the datasets. Afterward, the
PostgreSQL databases must be deleted, since new databases like data1,
data2, etc., will be created again.