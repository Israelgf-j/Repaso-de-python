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
    print("\n\tTabla 'inventario' creada exitosamente.")

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
        #print("\n\t1 Archivo Abierto ---")
        #print("\n\n\tEncabezados:")
        encabezados_csv = lector_csv.fieldnames
        #print(encabezados_csv, end="\n\n")

        # Saltar encabezados
        # print("\n\n\tPrimera fila:")
        # primera_fila = next(lector_csv)
        # print(primera_fila)
        # print(primera_fila["Last Move Date"])

        
        for fila in lector_csv:
            """
            #print("CSV:", fila["Last Move Date"])
            #fecha1 = convertir_fecha(fila["Last Move Date"])
            #fecha2 = convertir_fecha(fila["FIFO Date"])
            #fecha3 = convertir_fecha(fila["Manufactured Date"])
            #fecha4 = convertir_fecha(fila["Received Date"])
            #print("SQLite:", fecha)
            #print()

            
            fila_transformada = (
                fila["Building ID"],
                fila["Item Number"],
                fila["Description"],
                float(fila["Unit Quantity"]),
                fila["Stocking Unit of Measure"],
                fila["Lot Number"],
                fila["Inventory Status"],
                fila["Storage Location"],
                fila["Load Number"],
                fecha2,
                fecha1,
                fila["Supplier Lot Number"],
                fila["Display Unit Quantity"],
                fila["Area"],
                fecha3,
                fecha4
            )"""

            fila_sqlite = {}

            #print("\n\tDatos del archivo CSV: ".capitalize())
            #print(fila, sep="\n\n")
            
            for columna_sqlite, columna_csv in mapeo_encabezados.items():

                valor = fila[columna_csv]   # Toma de toda la 1ra fila de tu archivo CSV, toma el valor que coincida con la clave fila[columna_csv], que sera segun el diccionario "mapeo_encabezados" definido antes, el "valor" almacena el dato que este en la lista y cumpla con el encabezado que le toque en la iteracion.
                columnas_faltantes = []

                if columna_sqlite == "unit_quantity":
                    try:
                        valor = float(valor)
                    except ValueError:
                        valor = None

                elif columna_sqlite in ("fifo_date", "last_move_date", "manufactured_date", "received_date"):
                    try:
                        valor = convertir_fecha(valor)
                    except ValueError:
                        valor = None

                fila_sqlite[columna_sqlite] = valor

                if columna_csv not in columna_csv:
                    columnas_faltantes.append(columna_csv)
                    print("\n\t Faltan columnas:")

                if columnas_faltantes:
                    raise ValueError(f"Faltan columnas requeridas en el CVS: {columnas_faltantes}")
                
            #print(fila_transformada)
            #print(fila_sqlite)

            fila_transformada = tuple(fila_sqlite[columna] for columna in mapeo_encabezados.keys())
            #print(sep="\n\n")

            #print("\n\t Datos del sqlite:".capitalize())
            #print(fila_transformada)

            if fila[columna_csv] == "unit_quantity" and isinstance(fila[columna_csv], float) == False:
                print(f"\n\tLos datos de 'unit_quantity' deben ser tipo: float")
                break

            
            
            # Inserción masiva a sqlite
            cursor.execute("""
                INSERT INTO inventario (
                building_id,
                item_number,
                description,
                unit_quantity,
                stocking_unit_of_measure,
                lot_number,
                inventory_status,
                storage_location,   
                load_number,
                fifo_date,        
                last_move_date,
                supplier_lot_number,
                display_unit_quantity,
                area,
                manufactured_date,
                received_date
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", fila_transformada)


            """print("\n\t------------ Impresion de prueba ------------\n",
                fila["Building ID"],
                fila["Item Number"],
                fila["Description"],
                fila["Unit Quantity"],
                fila["Stocking Unit of Measure"],
                fila["Lot Number"],
                fila["Inventory Status"],
                fila["Storage Location"],
                fila["Load Number"],
                fecha2,
                fecha1,
                fila["Supplier Lot Number"],
                fila["Display Unit Quantity"],
                fila["Area"],
                fecha3,
                fecha4,
                sep="\n"
                )"""

            

            

        connection.commit()
        
        
    # Guardar cambios
    
    print("\n\t¡Éxito! Se han importado correctamente las filas del CSV.\n")

    # 5. Creamos el SELECT
    # NOTA: el LIMIT va al final de todo

    """
    cursor.execute(
    SELECT load_number, item_number, unit_quantity, stocking_unit_of_measure, last_move_date
    FROM inventario
    WHERE unit_quantity > 1000
    ORDER BY last_move_date
    LIMIT 10
    ) """

    print("\n\tTotal de datos leidos de la base de datos.")
    cursor.execute("SELECT COUNT(*) FROM inventario LIMIT 5")

    print(cursor.fetchall())

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
