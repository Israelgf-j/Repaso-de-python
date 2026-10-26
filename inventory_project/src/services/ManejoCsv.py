import os
import csv
from datetime import datetime

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


