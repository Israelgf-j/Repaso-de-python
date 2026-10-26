import os

# 1. Encuentra la carpeta 'src/' (donde vive config.py)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Sube un nivel ('..'). Ahora está parado en la raíz: 'inventory_project/'
RAIZ_PROYECTO = os.path.abspath(os.path.join(SRC_DIR, ".."))

# 3. Define la ruta DIRECTA a las carpetas contenedoras
DIR_DATABASE = os.path.join(RAIZ_PROYECTO, "database")  # Apunta a: inventory_project/database/
DIR_DATA = os.path.join(RAIZ_PROYECTO, "data")          # Apunta a: inventory_project/data/
