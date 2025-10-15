Um den install.sh Script ausfürbar zu machen muss mit "sudo apt install dos2unix" dos2unix installiert werden.
danach wird das script mit "chmod +x install.sh" ausführbar  gemacht.

nun kann das script ausgeführt werden mit "./install.sh"

WICHTIG:
    die scripts erwarten als user VMadmin. wenn dies nicht der user ist dann kann das einfach in den scripts geändert werden

es wird im laufe der installation im ordner nominatim ein verzeichniss namens nominatim-project erstellt.
hier kommen alle scripte rein (MASTER.py,info.txt,searchAllNode.py,round.py,reverse.py)

die anzahl der parallel laufenden threads können je nach system specs angepasst werden. 
Dafür  kann einvach die variable "MAX_THREADS" in MASTER.py geändert werden 

nach dem ausführen aller schritte werden csv dateien erstellt die jeweils alle straßennamen,PLZ,und städte der datensets enthalten
danach müssen die postgres datenbanken wieder gelöscht werden da erneut data1, data2 usw. erstellt werden.