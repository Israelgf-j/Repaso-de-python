import csv
from dataclasses import dataclass, asdict
from datetime import datetime



@dataclass
class RegistroDatos:
    Building_ID: str
    Item_Number: int
    Description: str
    Unit_Quantity: float
    Stocking_Unit_of_Measure: str
    Lot_Number: str
    Inventory_Status: str
    Storage_Location: str
    Load_Number: str
    FIFO_Date: str
    Last_Move_Date: str

    def __str__(self):
        return f"{self.__class__.__name__}:\n{asdict(self)}"


class CargadorCSV:
    def __init__(self, ruta_archivo: str):
        self.ruta = ruta_archivo
        self.datos: list[RegistroDatos] = []

    def cargar_datos(self):
        self.datos.clear()

        with open(self.ruta, mode="r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo, delimiter=",")

            for fila in lector:

                objeto = RegistroDatos(
                    Building_ID=fila["Building ID"],
                    Item_Number=int(fila["Item Number"]),
                    Description=fila["Description"],
                    Unit_Quantity=float(fila["Unit Quantity"]),
                    Stocking_Unit_of_Measure=fila["Stocking Unit of Measure"],
                    Lot_Number=fila["Lot Number"],
                    Inventory_Status=fila["Inventory Status"],
                    Storage_Location=fila["Storage Location"],
                    Load_Number=fila["Load Number"],
                    FIFO_Date=fila["FIFO Date"],
                    Last_Move_Date=datetime.strptime(fila["Last Move Date"], "%m/%d/%Y %I:%M:%S %p")
                )

                self.datos.append(objeto)

        return self.datos


class FiltroReporte:
    def __init__(self, registro: list):
        self.registro = registro

    def filtrar_por_storage_location(self, storage_location: str):
        # 1. Limpiamos el texto y lo pasamos a mayúsculas
        busqueda = storage_location.strip().upper()

            # 2. Verificamos si el usuario usó el comodín '%' al final
        if busqueda.endswith('%'):
            # Quitamos el '%' para obtener el texto base (ej. "A1%" se convierte en "A1")
            texto_base = busqueda[:-1]
            
            return [
                registro
                for registro in self.registro
                if registro.Storage_Location.upper().startswith(texto_base)
            ]
        
        # 3. Si no usó '%', hacemos la búsqueda exacta como antes
        return [
            registro
            for registro in self.registro
            if registro.Storage_Location.upper() == busqueda
        ]

    def filtrar_por_item(self, item: int):
            return [
                registro
                for registro in self.registro
                if registro.Item_Number == item
            ]
        
    def filtrar_registros(self, storage_location: str = None, item: int = None):

        # 1. Pre-procesar el filtro de Storage Location (Soporta múltiples valores separados por coma)
        patrones_sl = []

        if storage_location:
            # Separamos por coma por si quieres buscar "A1%, A2%"
            for termino in storage_location.split(','):
                termino_limpio = termino.strip().upper()
                if not termino_limpio:
                    continue
                
                # Detectamos si es búsqueda parcial (%) o exacta
                if termino_limpio.endswith('%'):
                    patrones_sl.append(('EMPIEZA', termino_limpio[:-1]))
                # Esta parte toma todos los valores que terminen con XXXX [Lo que haya dentreo de patrones, Ej. Patrones = A1, dara 100A1, 101A1]
                #elif termino_limpio.startswith('%'):
                #    patrones_sl.append(('TERMINA', termino_limpio[1:]))
                else:
                    patrones_sl.append(('EXACTO', termino_limpio))

        # Si no hay ningún filtro, regresamos todo de inmediato sin iterar
        if not (patrones_sl):
            return self.registro

        # 2. UN SOLO RECORRIDO para máxima velocidad, aqui comienza el verdadero filtrado.
        resultados = []
        for r in self.registro:
            # Evaluar Storage Location (Búsqueda "OR": si cumple CUALQUIERA de los patrones, pasa)
            if patrones_sl:
                # Recuerda que al iterar una lista de objetos, el valor que itera cada elemento de la lista, se convierte en un objeto, por eso puedes entrar a sus atributos, como en r.Storage_Location
                valor_r = r.Storage_Location.upper()
                cumple_sl = False
                
                for tipo, texto in patrones_sl:
                    if tipo == 'EMPIEZA' and valor_r.startswith(texto):
                        cumple_sl = True
                        break  # Con que cumpla uno, es suficiente
                
                    #elif tipo == 'TERMINA' and valor_r.endswith(texto):
                    #    cumple_sl = True
                    #    break
                
                    elif tipo == 'EXACTO' and valor_r == texto:
                        cumple_sl = True
                        break
                
                if not cumple_sl: 
                    continue # Si no cumplió ningún patrón de ubicación, saltamos al siguiente registro

            # Evaluar Item (Búsqueda "AND")
            if item and r.Item_Number != item:
                continue

            # Si pasó todos los filtros activos, se agrega al resultado
            resultados.append(r)

        return resultados

    def reporte_24hrs(self, reporte: FiltroReporte):
        # Reporte de 24hrs
        reporte_24hrs = []
        # 2. Obtener la fecha de HOY de forma automática (solo Año, Mes y Día)
        hoy = datetime(2026, 9, 5)     #.today().date() 

        # Datos de Supply
        #Localidades_supply = reporte.filtrar_registros("A1%, A2%")
        Localidades_paso_supply = reporte.filtrar_registros("ASH%, AST%, HO0%, HO1%")

        # Datos de Warehouse
        #Localidades_warehouse = reporte.filtrar_registros("B1%, C1%, D1%")
        Localidades_paso_warehouse = reporte.filtrar_registros("BRC%, BLD%, HOI%")

        reporte_24hrs = [*Localidades_paso_supply, *Localidades_paso_warehouse]

        # Ya hicimos la separacion de los datos, ahora falta filtrarlos por fechas diferentes a TODAY, si puede meter el filtro en un solo recorrido sin necesidad de meter otro bucle, adelante
        #fechas = [datetime.strptime(fecha, "%d/%m/%Y %H:%M") for fecha in reporte_24hrs.Last_Move_Date]
        data = []
        for r in reporte_24hrs:
            # Convertimos el texto a datetime
            #fecha_objeto = datetime.strptime(r.Last_Move_Date, "%d/%m/%Y %H:%M")

            # Extraemos solo la parte de la fecha (sin horas) para comparar
            if r.Last_Move_Date.date() != hoy:
                data.append(r)

        return data
    

class ExportarCSV:
    def __init__(self):
        pass

    def exportar_csv(self, reporte: list):

        if reporte:  # Verificamos que la lista no esté vacía
            
            # Convertimos todos tus objetos a una lista de diccionarios puros
            datos_diccionario = [asdict(registro) for registro in reporte]
            
            # Extraemos automáticamente los nombres de tus 10+ atributos para las columnas
            columnas = datos_diccionario[0].keys()

            # Creamos y escribimos el archivo CSV
            nombre_archivo = input("\n\tIngrese el nombre del archivo: ")
            
            with open(nombre_archivo, "w", newline="", encoding="utf-8-sig") as archivo:
                # Usamos 'utf-8-sig' para que Excel abra las tildes y la 'ñ' correctamente
                escritor = csv.DictWriter(archivo, fieldnames=columnas)
                
                escritor.writeheader()      # Escribe la fila de títulos (columnas)
                escritor.writerows(datos_diccionario) # Escribe todas las filas con tus datos

            print(f"\n\t¡Listo! Tus datos se exportaron correctamente a '{nombre_archivo}'.\n")
        else:
            print("\n\tLa lista está vacía, no hay nada que exportar.\n")



# Cargamos el archivo al programa
cargador = CargadorCSV("01 Files/Data.csv")

# Guardamos los datos del archivo en una variable
datos = cargador.cargar_datos()
base_datos = FiltroReporte(datos)


rep_24 = base_datos.reporte_24hrs(base_datos)


"""
# Aplicamos los filtros por localidad
filtro_sloc = base_datos.filtrar_por_storage_location("RTN%")

for registro in filtro_sloc:
    print(registro)

print(len(filtro_sloc))
"""

# Aplicamos los filtros por item
#filtro_item = base_datos.filtrar_por_item(21290744)
#print(len(filtro_item))

# Aplicamos doble filtro, localidad e item
#filtro_IySloc = base_datos.filtrar_registros("HOI%", 80850718)
#filtro_IySloc = base_datos.filtrar_registros("A1%, A2%, ASH%, AST%", 80804473)

#for r in rep_24:
#    print(r)

print(len(rep_24))

#for registro in filtro_item:
#    print(registro)

#archivo = ExportarCSV()
#archivo.exportar_csv(filtro_item)

