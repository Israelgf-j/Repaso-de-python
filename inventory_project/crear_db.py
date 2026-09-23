import csv
import os
import sqlite3

# Rutas del proyecto
ruta_csv = './inventory_project/data/inventory.csv'  # <--- Cambia esto por tu archivo real
ruta_db = './inventory_project/database/inventory.db'

# Asegurar que la carpeta de la base de datos exista
os.makedirs(os.path.dirname(ruta_db), exist_ok=True)

# 1. Conectar a la base de datos (se crea el archivo automáticamente aquí)
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# 2. Abrir y leer el archivo CSV
with open(ruta_csv, 'r', encoding='utf-8') as f:
    lector_csv = csv.reader(f)
    
    # Obtener la primera fila (los encabezados de las columnas)
    columnas = next(lector_csv)
    
    # Crear la tabla usando esos encabezados (todos se guardan como TEXT inicialmente)
    definicion_columnas = ", ".join([f"[{col.strip()}] TEXT" for col in columnas])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS productos ({definicion_columnas})")
    
    # 3. Insertar todas las filas del CSV en la tabla
    signos_interrogacion = ", ".join(["?"] * len(columnas))
    cursor.executemany(f"INSERT INTO productos VALUES ({signos_interrogacion})", lector_csv)

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
print("¡Base de datos creada y CSV importado con éxito!")
