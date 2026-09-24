import sqlite3
import os
import csv
from datetime import datetime

# 1. Rutas absolutas calculadas dinámicamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, '..', 'database', 'inventory.db')
RUTA_CSV = os.path.join(BASE_DIR, '..', 'data', 'inventory.csv')

connection = None


def convertir_fecha(fecha):

    if not fecha:
        return None

    fecha_datetime = datetime.strptime(fecha, "%m/%d/%Y %I:%M:%S %p")

    return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")


try:
    # 2. Conexión a la base de datos
    connection = sqlite3.connect(RUTA_DB)
    cursor = connection.cursor()
    print("Base de datos conectada correctamente.")

    # 3. Limpieza y creación de la tabla, tu la diseñas y decides como se llama cada columna
    cursor.execute("DROP TABLE IF EXISTS inventario;")
    
    cursor.execute("""
    CREATE TABLE inventario (
        building_id TEXT,
        item_number TEXT,
        description TEXT,
        unit_quantity REAL,
        stocking_unit_of_measure TEXT,
        lot_number TEXT,
        inventory_status TEXT,
        storage_location TEXT,
        load_number TEXT,
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

    mapeo_encabezados = {
        "building_id": "Building ID",
        "item_number": "Item Number",
        "description": "Description",
        "unit_quantity": "Unit Quantity",
        "stocking_unit_of_measure": "Stocking Unit of Measure",
        "lot_number": "Lot Number",
        "inventory_status": "Inventory Status",
        "storage_location": "Storage Location",
        "load_number": "Load Number",
        "fifo_date": "FIFO Date",
        "last_move_date": "Last Move Date",
        "supplier_lot_number": "Supplier Lot Number",
        "display_unit_quantity": "Display Unit Quantity",
        "area": "Area",
        "manufactured_date": "Manufactured Date",
        "received_date": "Received Date"
    }

    # 4. Leer el CSV e insertar los datos
    print(f"\n\tAbriendo archivo CSV en: {RUTA_CSV}...")
    with open(RUTA_CSV, 'r', encoding='utf-8', newline="") as f:

        lector_csv = csv.DictReader(f)
        print("\n\n\tEncabezados:")
        print(lector_csv.fieldnames)

        # Saltar encabezados
        print("\n\n\tPrimera fila:")
        primera_fila = next(lector_csv)
        print(primera_fila["Last Move Date"])
        print(primera_fila)

        for fila in lector_csv:
            print("CSV:", fila["Last Move Date"])
            fecha = convertir_fecha(fila["Last Move Date"])
            print("SQLite:", fecha)




        # Inserción masiva
        sql_insert = "INSERT INTO inventario VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"
        cursor.executemany(sql_insert, lector_csv)
        
    # Guardar cambios
    connection.commit()
    print("\n\t¡Éxito! Se han importado correctamente las filas del CSV.\n")

    # 5. Creamos el SELECT
    # NOTA: el LIMIT va al final de todo

    """ cursor.execute(
    SELECT load_number, item_number, unit_quantity, stocking_unit_of_measure, last_move_date
    FROM inventario
    WHERE unit_quantity > 1000
    ORDER BY last_move_date
    LIMIT 10
    ) """

    """cursor.execute(
    SELECT last_move_date, substr(last_move_date, 6, 4) || '-' || substr(last_move_date, 1, 1) || '-' || substr(last_move_date, 3, 2)
    FROM inventario
    LIMIT 5
    )"""


except sqlite3.OperationalError as e:
    print(f"\n\tError de SQLite: {e}")
except FileNotFoundError:
    print(f"\n\tError: No se encontró el archivo CSV en la ruta: {RUTA_CSV}")
except Exception as e:
    print(f"\n\tOcurrió un error inesperado: {e}")
finally:
    # 5. Cierre seguro de la conexión
    if connection:
        connection.close()
        print("\n\tConexión a la base de datos cerrada.")
