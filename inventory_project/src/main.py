import sqlite3
import os
import csv
from datetime import datetime


class Imprtador_inventario:
    def __init__(self):
        # 1. Rutas absolutas calculadas dinámicamente
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.RUTA_DB = os.path.join(self.BASE_DIR, '..', 'database', 'inventory.db')
        self.RUTA_CSV = os.path.join(self.BASE_DIR, '..', 'data', 'inventory.csv')
        self.connection = None
        self.cursor = None
        self.fila_transformada = ()


    def __enter__(self):
            self.connection = sqlite3.connect(self.RUTA_DB)
            self.cursor = self.connection.cursor()
            print("\n\tBase de datos conectada correctamente.") 
    
            return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.commit()  # Asegura guardar los últimos cambios
            self.connection.close()   # Cierra la conexión de forma segura
            print("\n\tConexión a la base de datos cerrada automáticamente.")


    def leer_CSV(self):
        try:
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
                "last_move_date": "Last Move Date"
            }

            """ 
            "supplier_lot_number": "Supplier Lot Number",
            "display_unit_quantity": "Display Unit Quantity",
            "area": "Area",
            "manufactured_date": "Manufactured Date",
            "received_date": "Received Date"
             """
            
            # 4. Leer el CSV e insertar los datos
            print(f"\n\tAbriendo archivo CSV en: {self.RUTA_CSV}...")
            with open(self.RUTA_CSV, 'r', encoding='utf-8-sig', newline="") as f:
        
                lector_csv = csv.DictReader(f)
                encabezados_csv = lector_csv.fieldnames

                for fila in lector_csv:
                
                    fila_sqlite = {}
                    
                    for columna_sqlite, columna_csv in mapeo_encabezados.items():
        
                        valor = fila[columna_csv]
                        columnas_faltantes = []
        
                        if columna_sqlite == "unit_quantity":
                            try:
                                valor = float(valor)
                            except ValueError:
                                valor = None
        
                        elif columna_sqlite in ("fifo_date", "last_move_date", "manufactured_date", "received_date"):
                            try:
                                valor = self.transformar_datos(valor)
                            except ValueError:
                                valor = None
        
                        fila_sqlite[columna_sqlite] = valor
        
                        if columna_csv not in columna_csv:
                            columnas_faltantes.append(columna_csv)
                            print("\n\t Faltan columnas:")
        
                        if columnas_faltantes:
                            raise ValueError(f"Faltan columnas requeridas en el CVS: {columnas_faltantes}")
                        
                    self.fila_transformada = tuple(fila_sqlite[columna] for columna in mapeo_encabezados.keys())
        
                    if fila[columna_csv] == "unit_quantity" and isinstance(fila[columna_csv], float) == False:
                        print(f"\n\tLos datos de 'unit_quantity' deben ser tipo: float")
                        break
                    
        except FileNotFoundError:
            print(f"\n\tError: No se encontró el archivo CSV en la ruta: {self.RUTA_CSV}")


    def transformar_datos(self, fecha):
        if not fecha:
            return None

        fecha_datetime = datetime.strptime(fecha, "%m/%d/%Y %I:%M:%S %p")

        return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")

    
    def crear_tabla(self):
        self.cursor.execute("DROP TABLE IF EXISTS inventario;")
        
        self.cursor.execute("""
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
            last_move_date TEXT
            );       
        """)

        """
            supplier_lot_number TEXT,
            display_unit_quantity TEXT,
            area TEXT,
            manufactured_date TEXT,
            received_date TEXT);
        """

        print("\n\tTabla 'inventario' creada exitosamente.")


    def insertar_datos(self):
        # Inserción masiva a sqlite
        self.cursor.execute("""
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
            fifo_date
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)""", self.fila_transformada) # ?,?,?,?,?,?

        """
        last_move_date,
        supplier_lot_number,
        display_unit_quantity,
        area,
        manufactured_date,
        received_date
        """

        print("\n\t¡Éxito! Se han importado correctamente las filas del CSV.\n")


    def total_inventario(self):
        print("\n\tTotal de datos leidos de la base de datos.")
        self.cursor.execute("SELECT COUNT(*) FROM inventario")
        
        return self.cursor.fetchall()


    def mostrar_datos(self):
        self.cursor.execute("""
            SELECT load_number, item_number, unit_quantity, stocking_unit_of_measure, last_move_date
            FROM inventario
            WHERE unit_quantity > 1000
            ORDER BY last_move_date
            LIMIT 10
            """)

        return self.cursor.fetchall()


def main():
    # 1. Abrimos aqui de forma automatica la conexion a la base de datos.
    with Imprtador_inventario() as gestor:

        print(gestor.fila_transformada)
        # Leemos el archivo CSV
        gestor.leer_CSV()
        print(gestor.fila_transformada)

        # 2. Creamos la tabla
        gestor.crear_tabla()

        # 3. Total de inventario en la base de datos
        total = gestor.total_inventario()
        print(total)

        # Primeros datos dentro de nuestra tabla
        datos = gestor.mostrar_datos()
        print(datos)


if __name__ == "__main__":
    main()