import sqlite3
import os
import csv

# 1. Rutas absolutas calculadas dinámicamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, '..', 'database', 'inventory.db')
RUTA_CSV = os.path.join(BASE_DIR, '..', 'data', 'inventory.csv')

connection = None

try:
    # 2. Conexión a la base de datos
    connection = sqlite3.connect(RUTA_DB)
    cursor = connection.cursor()
    print("Base de datos conectada correctamente.")

    # 3. Limpieza y creación de la tabla
    cursor.execute("DROP TABLE IF EXISTS inventario;")
    
    cursor.execute("""
    CREATE TABLE inventario (
        building_id TEXT,
        item_number TEXT,
        description TEXT,
        unit_quantity INTEGER,
        stocking_unit_of_measure TEXT,
        lot_number TEXT,
        inventory_status TEXT,
        storage_location TEXT,
        load_number TEXT PRIMARY KEY,
        fifo_date TEXT,        
        last_move_date TEXT,
        supplier_lot_number TEXT,
        display_unit_quantity TEXT,
        area TEXT,
        manufactured_date TEXT,
        received_date TEXT
    );
    """)
    print("Tabla 'inventario' creada exitosamente.")

    # 4. Leer el CSV e insertar los datos
    print(f"Abriendo archivo CSV en: {RUTA_CSV}...")
    with open(RUTA_CSV, 'r', encoding='utf-8') as f:
        lector_csv = csv.reader(f)
        
        # Saltar encabezados
        next(lector_csv)
        
        # Inserción masiva
        sql_insert = "INSERT INTO inventario VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        cursor.executemany(sql_insert, lector_csv)
        
    # Guardar cambios
    connection.commit()
    print("¡Éxito! Se han importado correctamente las filas del CSV.")

except sqlite3.OperationalError as e:
    print(f"Error de SQLite: {e}")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo CSV en la ruta: {RUTA_CSV}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")
finally:
    # 5. Cierre seguro de la conexión
    if connection:
        connection.close()
        print("Conexión a la base de datos cerrada.")
