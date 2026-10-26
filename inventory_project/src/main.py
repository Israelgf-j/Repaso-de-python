import sqlite3
import os
import sys
from src.queries.consultas import *
from src.services.ManejoCsv import ManejoCSV
from src.services.Importador import crear_tabla_capacidad, crear_tabla_productividad

# Sube un nivel desde 'src/' para encontrar la raíz del proyecto
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)

from src.settings.Capacidad import mapeo_capacidad
from src.settings.Productividad import mapeo_productividad


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


    def imprimir_datos(self, consulta):
        if consulta: # Verificamos que la consulta no este vacia
            # 1. Extraemos los encabezados de la primera fila.
            encabezados = consulta[0].keys()
            print(" | ".join(encabezados))      # Imprime : id | item | qty
            print("-" * 130)

            # 2. Iteramos el resto de las filas de forma limpia
            for row in consulta[:10]:
                # Creamos una lista con los valores ordenados en cada columna
                valores = [str(row[col]) for col in encabezados]
                print(" | ".join(valores))


def main():
    nombre_csv_capacidad = 'Inv 24 Oct 2026.csv'
    nombre_csv_productividad = 'Productividad.csv'
    nombre_db_capacidad = 'Inv 24 Oct 2026.db'
    nombre_db_productividad = 'Productividad.db'

    with ImprtadorInventario(nombre_csv_productividad, nombre_db_productividad) as gestor:

        # ----------------------------------------- Trabajo de Capacidad del ALMACEN -----------------------------------------

        #crear_tabla_capacidad(gestor.cursor)
        #gestor.insertar_datos_capacidad()

        tabla_capacidad = "inventario_capacidad"

        #total = total_inventario(gestor.cursor, tabla_capacidad)
        #print(f"\t---------- Total real guardado en BD CAPACIDAD: {total} registros.")

        
        #datos_filtrados = mostrar_datos_tabla(gestor.cursor, tabla_capacidad)
        #print("\tPrimeros 10 datos de la consulta SQlite:\n\n")
        #gestor.imprimir_datos(datos_filtrados)



        #    ----------------- Reporte de 24 horas -----------------
        #rep24hrs = reporte_24hrs(gestor.cursor, tabla_capacidad)
        #gestor.imprimir_datos(rep24hrs)


        #    ----------------- Reporte de capacidad de almacen -----------------
        #repCapacidad = reporte_capacidad(gestor.cursor, tabla_capacidad)
        #gestor.imprimir_datos(repCapacidad)
        print()


        #ManejoCSV.exportar_a_csv(datos=rep24hrs, nombre_archivo="24_hrs.csv", exportar_a=gestor.BASE_DIR)
        #ManejoCSV.reporte_capacidad_segmentado(repCapacidad, exportar_a=gestor.BASE_DIR)


        # ----------------------------------------- Trabajo de Productividad -----------------------------------------

        tabla_productividad = "inventario_productividad"
        
        crear_tabla_productividad(gestor.cursor)
        gestor.insertar_datos_productividad()

        total = total_inventario(gestor.cursor, tabla_productividad)
        print(f"\tTotal real guardado en BD PRODUCTIVIDAD: {total} registros.")
        




if __name__ == "__main__":
    main()