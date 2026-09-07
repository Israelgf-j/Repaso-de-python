from abc import ABC
import json
import csv
from dataclasses import dataclass, asdict
from pprint import pprint


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
                    FIFO_Date=fila["FIFO Date"]
                )

                self.datos.append(objeto)

        return self.datos


class FiltroReporte:
    def __init__(self, registro: list):
        self.registro = registro

    def filtrar_por_storage_location(self, storage_location: str):
        return [
            registro
            for registro in self.datos
            if registro.Storage_Location == storage_location.strip().upper()
        ]

    def exportar_csv(self, reporte: list):

        if reporte:  # Verificamos que la lista no esté vacía
            
            # Convertimos todos tus objetos a una lista de diccionarios puros
            datos_diccionario = [asdict(registro) for registro in reporte]
            
            # Extraemos automáticamente los nombres de tus 10+ atributos para las columnas
            columnas = datos_diccionario[0].keys()

            # Creamos y escribimos el archivo CSV
            nombre_archivo = "registro_datos_exportado.csv"
            
            with open(nombre_archivo, "w", newline="", encoding="utf-8-sig") as archivo:
                # Usamos 'utf-8-sig' para que Excel abra las tildes y la 'ñ' correctamente
                escritor = csv.DictWriter(archivo, fieldnames=columnas)
                
                escritor.writeheader()         # Escribe la fila de títulos (columnas)
                escritor.writerows(datos_diccionario) # Escribe todas las filas con tus datos

            print(f"\n\t¡Listo! Tus datos se exportaron correctamente a '{nombre_archivo}'.\n")
        else:
            print("\n\tLa lista está vacía, no hay nada que exportar.\n")




cargador = CargadorCSV("01 Files/Data.csv")

datos = cargador.cargar_datos()

resultados = cargador.filtrar_por_storage_location("RTNTTD")

for registro in resultados:
    print(registro)