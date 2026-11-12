import sqlite3
import os
import sys
import argparse  # <-- Librería clave para manejar la terminal de forma elegante
from src.queries.consultas import *
from src.services.Importador import *
from src.services.Reportes import *
from src.config import DIR_DATABASE, DIR_DATA

# Sube un nivel desde 'src/' para encontrar la raíz del proyecto
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ruta_raiz)


class ImprtadorInventario:

    def __init__(self, db_name):
        self.RUTA_DB = os.path.join(DIR_DATABASE, db_name)
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.RUTA_DB)
        self.connection.row_factory = sqlite3.Row   
        self.cursor = self.connection.cursor()
        print(f"\n\tBase de datos [{os.path.basename(self.RUTA_DB)}] conectada correctamente.") 
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit() 
        else:
            self.connection.rollback()
        
        self.cursor.close()
        self.connection.close()
        print("\tConexión a la base de datos cerrada automáticamente.\n")

    def imprimir_datos(self, consulta):
        if consulta: 
            encabezados = consulta[0].keys()
            print("  |  ".join(encabezados))      
            print("-" * 130)
            for row in consulta[:10]:
                valores = [str(row[col]) for col in encabezados]
                print(" | ".join(valores))


# --- Bloques de código encapsulados en funciones independientes ---

def ejecutar_reporte_24hrs(nombre_csv_capacidad):
    tabla_capacidad = "inventario_capacidad"
    with ImprtadorInventario('Capacidad.db') as gestor:
        crear_tabla_capacidad(gestor.cursor)
        insertar_datos_capacidad(gestor.cursor, nombre_csv_capacidad)
        
        print("\n\t[PROCESANDO] Generando Reporte de 24 horas...")
        rep24hrs = reporte_24hrs(gestor.cursor, tabla_capacidad)
        gestor.imprimir_datos(rep24hrs)
        
        ManejoCSV.exportar_a_csv(datos=rep24hrs, nombre_archivo="24_hrs.csv", exportar_a=DIR_DATA)


def ejecutar_reporte_capacidad(nombre_csv_capacidad):
    tabla_capacidad = "inventario_capacidad"
    with ImprtadorInventario('Capacidad.db') as gestor:
        crear_tabla_capacidad(gestor.cursor)
        insertar_datos_capacidad(gestor.cursor, nombre_csv_capacidad)
        
        print("\n\t[PROCESANDO] Generando Reporte de Capacidad...")
        repCapacidad = reporte_capacidad(gestor.cursor, tabla_capacidad)
        gestor.imprimir_datos(repCapacidad)
        
        ManejoCSV.reporte_capacidad_segmentado(repCapacidad, exportar_a=DIR_DATA)


def ejecutar_reporte_productividad(nombre_csv_productividad):
    tabla_productividad = "inventario_productividad"
    with ImprtadorInventario('Productividad.db') as gestor:
        crear_tabla_productividad(gestor.cursor)
        insertar_datos_productividad(gestor.cursor, nombre_csv_productividad)

        total = total_inventario(gestor.cursor, tabla_productividad)
        print(f"\tTotal real guardado en BD PRODUCTIVIDAD: {total} registros.")

        reporte1 = extraer_datos(gestor.cursor, tabla_productividad)
        print(f"\tTipo de dato compartido: {type(reporte1[0])}")
        print(f"\tTotal de registros: {len(reporte1)}")
        gestor.imprimir_datos(reporte1)
        
        print("\n\t[PROCESANDO] Generando Reporte de Productividad...")
        resultado = resumen_productividad_por_usuario(reporte1)
        mostrar_reporte_en_pantalla(resultado)


def main():
    # 1. Configuración del menú de ayuda de la terminal
    parser = argparse.ArgumentParser(
        description="Sistema de Reportes de Inventario y Productividad.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 2. Definición del argumento principal (el tipo de reporte)
    parser.add_argument(
        '--reporte', 
        choices=['24hrs', 'capacidad', 'productividad'], 
        required=True,
        help="Elige el tipo de reporte que deseas ejecutar:\n"
             "  24hrs         - Genera el reporte de 24 horas de capacidad.\n"
             "  capacidad     - Genera el reporte segmentado de capacidad.\n"
             "  productividad - Genera el reporte analítico de productividad."
    )

    # 3. Leer los comandos escritos en la terminal
    args = parser.parse_args()

    # Nombres de archivos base (puedes cambiarlos aquí centralizadamente)
    nombre_csv_capacidad = 'Inv 10 Nov 2026.csv'
    nombre_csv_productividad = 'Productividad 27 - 10 2026 OMAR.csv'

    # 4. Orquestador: Dependiendo de lo que pida el usuario, ejecuta una función u otra
    if args.reporte == '24hrs':
        ejecutar_reporte_24hrs(nombre_csv_capacidad)
        
    elif args.reporte == 'capacidad':
        ejecutar_reporte_capacidad(nombre_csv_capacidad)
        
    elif args.reporte == 'productividad':
        ejecutar_reporte_productividad(nombre_csv_productividad)


if __name__ == "__main__":
    main()
