import sqlite3
import os
import csv
from datetime import datetime


class ImprtadorInventario:
    def __init__(self, csv_name, db_name):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.RUTA_DB = os.path.join(self.BASE_DIR, '..', 'database', db_name)
        self.RUTA_CSV = os.path.join(self.BASE_DIR, '..', 'data', csv_name)
        self.connection = None
        self.cursor = None


    def __enter__(self):
        self.connection = sqlite3.connect(self.RUTA_DB)
        self.connection.row_factory = sqlite3.Row   # cAMBIAMOS LA SALIDA DE DATOS DE 'TUPLAS' A 'DATOS TIPO ROW' ESTOS PERMITEN USAR .KYES PARA OBTENER LOS ENCABEZADOS DE DONDE SE CONSULTO LA INFORMACION.

        self.cursor = self.connection.cursor()
        print("\n\tBase de datos conectada correctamente.") 
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit() 
        else:
            self.connection.rollback()
        
        self.cursor.close()
        self.connection.close()
        print("\n\tConexión a la base de datos cerrada automáticamente.")

    
    def crear_tabla(self):
        self.cursor.execute("DROP TABLE IF EXISTS inventario;")
        query = """
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
            received_date TEXT);     
        """
        self.cursor.execute(query)
        print("\n\tTabla 'inventario' creada exitosamente.")


    def insertar_datos(self):
        fila_transformada, _ = ManejoCSV.leer_CSV(self.RUTA_CSV) # Convencion de uso de guion bajo para indicar que eso se ignora

        # 🌟 CORREGIDO: Inserción masiva usando 'executemany' para procesar la lista completa, aqui vamos a tratar de insertar dato a dato para evitar saturar la memoria cargandole todo un archivo de miles de lineas a una variable.
        query = """
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
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

        if fila_transformada:
            self.cursor.executemany(query, fila_transformada)
            print(f"\n\t¡Éxito! Se han importado correctamente {len(fila_transformada)} filas al inventario.\n")
        else:
            print("\n\tAdvertencia: No hay datos para insertar.")


    def total_inventario(self):
        query = "SELECT COUNT(*) FROM inventario"
        self.cursor.execute(query)
        # 🌟 OPTIMIZACIÓN: Retornamos directamente el entero en lugar de la estructura completa
        return self.cursor.fetchone()[0]


    def imprimir_datos(self, consulta):
        if consulta: # Verificamos que la consulta no este vacia
            # 1. Extraemos los encabezados de la primera fila.
            encabezados = consulta[0].keys()
            print(" | ".join(encabezados))      # Imprime : id | item | qty
            print("-" * 30)

            # 2. Iteramos el resto de las filas de forma limpia
            for row in consulta:
                # Creamos una lista con los valores ordenados en cada columna
                valores = [str(row[col]) for col in encabezados]
                print(" | ".join(valores))
                

    def mostrar_datos(self):
        query = """
            SELECT load_number, item_number, unit_quantity, stocking_unit_of_measure, last_move_date
            FROM inventario
            WHERE unit_quantity > 1000
            ORDER BY last_move_date
            LIMIT 10
            """
        self.cursor.execute(query)
        datos = self.cursor.fetchall()
        return datos


    def reporte_24hrs(self):
        """
        Retorna registros filtrados por ubicaciones específicas (HO, AST, ASH, BRC, BLD) 
        y cuya fecha de último movimiento sea estrictamente anterior al día de hoy.
        """
        print("\n\tEjecutando consulta del reporte de 24 horas...")
        
        query = """
        SELECT load_number, item_number, unit_quantity, storage_location, supplier_lot_number, lot_number, last_move_date,
        -- 🌟 CORRECCIÓN: Compara puras fechas (substrae los días reales sin importar la hora)
        CAST(julianday(date('now', 'localtime')) - julianday(date(last_move_date)) AS INTEGER) AS dias_perdido 
        FROM inventario 
        WHERE ( 
            storage_location LIKE 'HO%' OR 
            storage_location LIKE 'AST%' OR 
            storage_location LIKE 'ASH%' OR 
            storage_location LIKE 'BRC%' OR 
            storage_location LIKE 'BLD%' 
        ) 
        -- 🌟 FILTRO SEGURO: Asegura que solo traiga días estrictamente anteriores (Ayer o antes)
        AND date(last_move_date) < date('now', 'localtime') 
        ORDER BY dias_perdido DESC;
        """
        
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def reporte_capacidad(self):
            """
            Retorna registros filtrados por ubicaciones específicas (B10, B11, B12, B13, B14, C10, C11, C12, C13, C14, D10, D11, D12, D13, D14, HOI, BRC, BLD, A1, A2 AST, ASH, HO1, HO0)
            """
            print("\n\tEjecutando consulta del reporte de capacidad...")
            
            query = """
            SELECT  building_id, item_number, description, unit_quantity, stocking_unit_of_measure, lot_number, inventory_status,storage_location, load_number, fifo_date
            FROM inventario 
            WHERE (
                -- Simplificación para patrones como B10, B11..., C10..., D10...
                (SUBSTR(storage_location, 1, 3) IN (
                    'B10', 'B11', 'B12', 'B13', 'B14', 
                    'C10', 'C11', 'C12', 'C13', 'C14', 
                    'D10', 'D11', 'D12', 'D13', 'D14', 
                    'HOI', 'BRC', 'BLD', 'HO1', 'HO0', 'AST', 'ASH'
                ))
                -- Simplificación para patrones más cortos de 2 caracteres
                OR (SUBSTR(storage_location, 1, 2) IN ('A1', 'A2'))
            );
            -- ORDER BY storage_location DESC;
            """

            self.cursor.execute(query)
            return self.cursor.fetchall()


    

class ManejoCSV:

    def __init__(self):
        raise TypeError("Esta clase es estática y no puede ser instanciada.")


    def transformar_datos(fecha):
        fecha_limpia = fecha.strip()

        # Intenta parsear el formato del CSV. Asegúrate de que coincida exactamente con tus datos
        fecha_datetime = datetime.strptime(fecha_limpia, "%m/%d/%Y %I:%M:%S %p")

        return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")


    @classmethod    # Usa este decorador o una clase estatica cuando no ocupes instanciar una clase, solo usar sus metodos pero que estos puedan acceder a sus propias propiedades (atributos o metodos)
    def leer_CSV(cls, RUTA_CSV):
            try:
                fila_transformada = []

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
                
                print(f"\n\tAbriendo archivo CSV en: {RUTA_CSV}...")
    
                with open(RUTA_CSV, 'r', encoding='utf-8-sig', newline="") as f:
                    lector_csv = csv.DictReader(f)
                    
                    encabezados_csv = lector_csv.fieldnames
                    columnas_faltantes = [col_csv for col_csv in mapeo_encabezados.values() if col_csv not in encabezados_csv]
                    if columnas_faltantes:
                        raise ValueError(f"Faltan columnas requeridas en el CSV: {columnas_faltantes}")
    
                    for fila in lector_csv:
                        fila_sqlite = {}
                        
                        for columna_sqlite, columna_csv in mapeo_encabezados.items():
                            valor = fila[columna_csv]
            
                            if columna_sqlite == "unit_quantity":
                                try:
                                    valor = float(valor)
                                except (ValueError, TypeError):
                                    valor = None  # O None, según prefieras
            
                            elif columna_sqlite in ("fifo_date", "last_move_date", "manufactured_date", "received_date"):
                                if valor is None or str(valor).strip() == "":
                                    valor = None
                                else:
                                    valor = cls.transformar_datos(str(valor))
                                
                            fila_sqlite[columna_sqlite] = valor
                        
                        nueva_tupla = tuple(fila_sqlite[columna] for columna in mapeo_encabezados.keys())

                        fila_transformada.append(nueva_tupla)

                    return fila_transformada, mapeo_encabezados

                print("\n\tDatos leídos del CSV (en memoria):", len(fila_transformada))
                        
            except FileNotFoundError:
                print(f"\n\tError: No se encontró el archivo CSV en la ruta: {RUTA_CSV}")
            except ValueError as e:
                print(f"\n\tError de validación: {e}")


    @staticmethod
    def exportar_a_csv(datos, nombre_archivo, exportar_a):
            """
            Exporta los datos de la última consulta a un archivo CSV 
            detectando encabezados automáticamente y añadiendo fecha/hora al nombre.
            """
            if not datos:
                print(f"\n\tAdvertencia: No hay datos para exportar.")
                return            

            # 1. Obtener los encabezados.
            encabezados = list(datos[0].keys())

            # Generamos el timestamp (Ej: 20261005_0922)
            timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
            
            # Separamos el nombre de la extensión para meter el timestamp en medio
            nombre_base, extension = os.path.splitext(nombre_archivo)
            if not extension:
                extension = ".csv"
                
            nombre_final = f"{nombre_base}_{timestamp}{extension}"
    
            # Ruta de salida dinámica con el nombre final
            ruta_salida = os.path.join(exportar_a, '..', 'data', nombre_final)
            
            try:
                os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
                
                with open(ruta_salida, 'w', encoding='utf-8-sig', newline="") as f:
                    escritor_csv = csv.writer(f)
                    
                    # Escribimos encabezados
                    escritor_csv.writerow(encabezados)

                    # Escribimos todas las filas. DictWriter acepta objetos sqlite3.Row directamente
                    escritor_csv.writerows(tuple(fila) for fila in datos)
                    
                print(f"\n\t¡Éxito! Consulta exportada correctamente a: {ruta_salida}")
                
            except Exception as e:
                print(f"\n\tError al exportar a CSV: {e}")
    



def main():
    nombre_csv = 'Inv 12 Oct 2026.csv'
    nombre_db = 'Inv 12 Oct 2026.db'

    with ImprtadorInventario(nombre_csv, nombre_db) as gestor:

        gestor.crear_tabla()
        gestor.insertar_datos()

        total = gestor.total_inventario()
        print(f"\tTotal real guardado en BD: {total} registros.")

        #datos_filtrados = gestor.mostrar_datos()
        #print(f"\tPrimeros 10 datos (con cantidad > 1000):\n\n", datos_filtrados)

        rep24hrs = gestor.reporte_24hrs()
        gestor.imprimir_datos(rep24hrs)

        # ------------- Ya realizamos la separacion del codigo en una clase mas, esta se encarga del manejo de todo lo que tiene que ver con CSV, ahora falta exportar de manera correcta los datos debido a que se cambio la manera en que se presentan las consultas del CSV, osea, el fetchall() ya no nos arroja una lista de tuplas, ahora se comporta como una lista de diccionarios, el desempaquetamiento debe ser acorde a esto. 
        # LISTO: ya no la complicamos tratando de hacer un metodo que exporte este nuevo tipo de dato complejo, simplemente convertimos ese tipo de dato complejo a una tupla sencilla y la insertamos de manera ordinaria
        
        #repCapacidad = gestor.reporte_capacidad()
        #gestor.imprimir_datos(repCapacidad)
        print()
        

        ManejoCSV.exportar_a_csv(datos=rep24hrs, nombre_archivo="24_hrs.csv", exportar_a=gestor.BASE_DIR)
        #ManejoCSV.exportar_a_csv(datos=repCapacidad, nombre_archivo="Inventario_General.csv", exportar_a=gestor.BASE_DIR)



if __name__ == "__main__":
    main()