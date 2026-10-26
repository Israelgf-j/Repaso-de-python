import os
from src.config import DIR_DATA
from src.settings.Capacidad import mapeo_capacidad
from src.settings.Productividad import mapeo_productividad
from src.services.ManejoCsv import ManejoCSV


def crear_tabla_capacidad(cursor):

    #_, claves_csv_bd = ManejoCSV.leer_CSV(self.RUTA_CSV
    cursor.execute("DROP TABLE IF EXISTS inventario_capacidad;")
    query = """
        CREATE TABLE inventario_capacidad (
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
        received_date TEXT);     
    """

    print("\n\tTabla 'inventario_capacidad' creada exitosamente.")
    
    return cursor.execute(query)


def crear_tabla_productividad(cursor):

    cursor.execute("DROP TABLE IF EXISTS inventario_productividad;")

    query = """
        CREATE TABLE inventario_productividad (
        from_location TEXT,
        to_location TEXT,
        activity_code TEXT,
        operation_code TEXT,
        user_id TEXT,
        item_number TEXT,
        last_updated_date TEXT,
        quantity REAL,
        load_number TEXT,
        lot_number TEXT,
        supplier_lot_number TEXT);
        """
    
    print("\n\tTabla 'inventario_productividad' creada exitosamente.")
    
    return cursor.execute(query)


def insertar_datos_capacidad(cursor, csv_name):
    # Construimos la ruta usando la configuración centralizada
    RUTA_CSV = os.path.join(DIR_DATA, csv_name)

    fila_transformada, claves_csv_bd = ManejoCSV.leer_CSV(RUTA_CSV, mapeo_capacidad)

    query = f"INSERT INTO inventario_capacidad ({',\n'.join(claves_csv_bd.keys())}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

    if fila_transformada:
        cursor.executemany(query, fila_transformada)
        print(f"\n\t¡Éxito! Se han importado correctamente {len(fila_transformada)} filas al inventario.\n")
    else:
        print("\n\tAdvertencia: No hay datos para insertar.")


def insertar_datos_productividad(cursor, csv_name):

    # Construimos la ruta usando la configuración centralizada
    RUTA_CSV = os.path.join(DIR_DATA, csv_name)

    fila_transformada, claves_csv_bd = ManejoCSV.leer_CSV(RUTA_CSV, mapeo_productividad)

    query = f"INSERT INTO inventario_productividad({',\n'.join(claves_csv_bd.keys())}) VALUES (?,?,?,?,?,?,?,?,?,?,?)"

    if fila_transformada:
        cursor.executemany(query, fila_transformada)
        print(f"\n\t¡Éxito! Se han importado correctamente {len(fila_transformada)} filas al inventario_productividad.\n")
    else:           
        print("\n\tAdvertencia: No hay datos para insertar.")
        