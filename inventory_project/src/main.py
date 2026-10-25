import sqlite3
import os
import sys
import csv
from datetime import datetime

# Sube un nivel desde 'src/' para encontrar la raíz del proyecto
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)

from settings.Capacidad import mapeo_capacidad
from settings.Productividad import mapeo_productividad

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


    # Pregunta si estaria bien crear esta tabla de manera automatica con todos los datos o si es mejor mantener esto manual y escoger que datos crear
    def crear_tabla_capacidad(self):
        #_, claves_csv_bd = ManejoCSV.leer_CSV(self.RUTA_CSV
        self.cursor.execute("DROP TABLE IF EXISTS inventario;")
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
        #query = f"INSERT INTO inventario ({' TEXT,\n'.join( [ v for v in claves_csv_bd.keys() ] )}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        self.cursor.execute(query)
        print("\n\tTabla 'inventario_capacidad' creada exitosamente.")


    def crear_tabla_productividad(self):
        self.cursor.execute("DROP TABLE IF EXISTS inventario_productividad;")
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
        
        self.cursor.execute(query)
        print("\n\tTabla 'inventario_productividad' creada exitosamente.")


    def insertar_datos_capacidad(self):
        fila_transformada, claves_csv_bd = ManejoCSV.leer_CSV(self.RUTA_CSV, mapeo_capacidad)

        query = f"INSERT INTO inventario_capacidad ({',\n'.join(claves_csv_bd.keys())}) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"

        if fila_transformada:
            self.cursor.executemany(query, fila_transformada)
            print(f"\n\t¡Éxito! Se han importado correctamente {len(fila_transformada)} filas al inventario.\n")
        else:
            print("\n\tAdvertencia: No hay datos para insertar.")


    def insertar_datos_productividad(self):
        fila_transformada, claves_csv_bd = ManejoCSV.leer_CSV(self.RUTA_CSV, mapeo_productividad)

        query = f"INSERT INTO inventario_productividad({',\n'.join(claves_csv_bd.keys())}) VALUES (?,?,?,?,?,?,?,?,?,?,?)"

        if fila_transformada:
            self.cursor.executemany(query, fila_transformada)
            print(f"\n\t¡Éxito! Se han importado correctamente {len(fila_transformada)} filas al inventario_productividad.\n")
        else:           
            print("\n\tAdvertencia: No hay datos para insertar.")


    def total_inventario(self, tabla):
        query = f"SELECT COUNT(*) FROM {tabla}"
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
                

    def mostrar_datos(self, tabla):
        query = f"""
            SELECT load_number, item_number, unit_quantity, stocking_unit_of_measure, last_move_date
            FROM {tabla}
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
            storage_location LIKE 'WHKILL%' OR
            storage_location LIKE 'HOI%' OR
            storage_location LIKE 'BRC%' OR 
            storage_location LIKE 'BLD%' OR
            storage_location LIKE 'HO0%' OR
            storage_location LIKE 'HO1%' OR
            storage_location LIKE 'AST%' OR
            storage_location LIKE 'ASH%' 
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


    @staticmethod
    def transformar_datos(fecha):
        if fecha is None or not fecha.strip():
            return None
        
        fecha_datetime = datetime.strptime(fecha, "%m/%d/%Y %I:%M:%S %p")

        return fecha_datetime.strftime("%Y-%m-%d %H:%M:%S")


    @classmethod    # Usa este decorador o una clase estatica cuando no ocupes instanciar una clase, solo usar sus metodos pero que estos puedan acceder a sus propias propiedades (atributos o metodos)
    def leer_CSV(cls, RUTA_CSV, mapeo_encabezados=None):
            try:
                if not os.path.exists(RUTA_CSV):
                    raise FileNotFoundError(f"El archivo CSV no existe en la ruta: {RUTA_CSV}")
                
                # Validar si el archivo está vacío
                if os.path.getsize(RUTA_CSV) == 0:
                    raise ValueError(f"El archivo CSV está vacío: {RUTA_CSV}")

                fila_transformada = []
                
                print(f"\n\tAbriendo archivo CSV en: {RUTA_CSV}...")
    
                with open(RUTA_CSV, 'r', encoding='utf-8-sig', newline="") as f:
                    lector_csv = csv.DictReader(f)
                    
                    #encabezados_csv = lector_csv.fieldnames
                    #mapeo_encabezados = {clave.strip().lower().replace(" ", "_"): clave for clave in encabezados_csv}
                    print("\n\tEncabezados:", mapeo_encabezados)

                    for fila in lector_csv:
                        fila_sqlite = {}

                        encabezados_csv = lector_csv.fieldnames or []

                        columnas_faltantes = [columna_csv for columna_csv in mapeo_encabezados.values() if columna_csv not in encabezados_csv]

                        if columnas_faltantes:
                            raise ValueError(f"Faltan encabezados requeridos: {columnas_faltantes}")
                        
                        for columna_sqlite, columna_csv in mapeo_encabezados.items():
                            valor = fila[columna_csv]
            
                            if columna_sqlite == "unit_quantity":
                                try:
                                    valor = float(valor)
                                except (ValueError, TypeError):
                                    valor = None  # O None, según prefieras
            
                            elif columna_sqlite in ("fifo_date", "last_move_date", "manufactured_date", "received_date"):
                                valor = cls.transformar_datos(valor)
                                
                            fila_sqlite[columna_sqlite] = valor
                        
                        nueva_tupla = tuple(fila_sqlite[columna] for columna in mapeo_encabezados.keys())

                        fila_transformada.append(nueva_tupla)

                    if not fila_transformada:
                        raise ValueError("El archivo CSV contiene encabezados pero no tiene registros de datos.")

                    print("\n\tDatos leídos del CSV (en memoria):", len(fila_transformada))
                    return fila_transformada, mapeo_encabezados
                        
            except Exception as e:
                print(f"\n\tError crítico procesando el CSV: {e}")
                raise  # Propagamos el error para que detenga la ejecución y no guarde basura en la BD


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


    @staticmethod
    def reporte_capacidad_segmentado(datos, exportar_a):
        """
        Ejecuta el reporte de capacidad y segmenta los resultados en 4 archivos CSV diferentes.
        """
        # 1. Traemos todos los datos con tu query original

        if not datos:
            print("\n\tNo se encontraron datos para segmentar.")
            return

        # 2. Definimos los 4 grupos de prefijos basados en tus reglas
        grupos = {
            "B10_D14": ['B10', 'B11', 'B12', 'B13', 'B14', 'C10', 'C11', 'C12', 'C13', 'C14', 'D10', 'D11', 'D12', 'D13', 'D14'],
            "HOI_BLD": ['HOI', 'BRC', 'BLD'],
            "A1_A2": ['A1', 'A2'],
            "HO1_ASH": ['HO1', 'HO0', 'AST', 'ASH']
        }

        # 3. Inicializamos contenedores vacíos para cada grupo y uno para los que no entren en ninguno
        datos_segmentados = {key: [] for key in grupos.keys()}
        datos_segmentados["Otros"] = []

        # 4. Clasificamos cada fila (evaluando los primeros 3 y 2 caracteres)
        for fila in datos:
            loc = fila['storage_location'] if fila['storage_location'] else ""
            prefijo_3 = loc[:3]
            prefijo_2 = loc[:2]
            
            asignado = False
            for nombre_grupo, prefijos in grupos.items():
                # Verificamos si coincide el prefijo de 3 o de 2 caracteres
                if prefijo_3 in prefijos or prefijo_2 in prefijos:
                    datos_segmentados[nombre_grupo].append(fila)
                    asignado = True
                    break
            
            if not asignado:
                datos_segmentados["Otros"].append(fila)

        # 5. Exportamos cada grupo usando tu método estático actual
        for nombre_grupo, filas_grupo in datos_segmentados.items():
            if filas_grupo: # Solo exporta si el grupo tiene registros
                nombre_archivo = f"reporte_capacidad_{nombre_grupo}.csv"
                # Llamamos a tu método tal y como está
                ManejoCSV.exportar_a_csv(filas_grupo, nombre_archivo, exportar_a)






def main():
    nombre_csv_capacidad = 'Inv 24 Oct 2026.csv'
    nombre_csv_productividad = 'Productividad.csv'
    nombre_db = 'Inv 24 Oct 2026.db'
    nombre_db_productividad = 'Productividad.db'

    with ImprtadorInventario(nombre_csv_capacidad, nombre_db) as gestor:

        gestor.crear_tabla_capacidad()
        gestor.insertar_datos_capacidad()

        tabla_productividad = "inventario_productividad"
        tabla_capacidad = "inventario_capacidad"

        total = gestor.total_inventario(tabla_capacidad)
        print(f"\tTotal real guardado en BD CAPACIDAD: {total} registros.")

        #datos_filtrados = gestor.mostrar_datos(tabla_capacidad)
        #print(f"\tPrimeros 10 datos (con cantidad > 1000):\n\n", datos_filtrados)

        #rep24hrs = gestor.reporte_24hrs()
        #gestor.imprimir_datos(rep24hrs)


        #gestor.crear_tabla_productividad()
        #gestor.insertar_datos_productividad()

        #total = gestor.total_inventario(tabla_productividad)
        #print(f"\tTotal real guardado en BD PRODUCTIVIDAD: {total} registros.")
        
        #repCapacidad = gestor.reporte_capacidad()
        #gestor.imprimir_datos(repCapacidad)
        print()


        #ManejoCSV.exportar_a_csv(datos=rep24hrs, nombre_archivo="24_hrs.csv", exportar_a=gestor.BASE_DIR)
        #ManejoCSV.reporte_capacidad_segmentado(repCapacidad, exportar_a=gestor.BASE_DIR)



if __name__ == "__main__":
    main()