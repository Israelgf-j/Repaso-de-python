from abc import ABC
import json
import csv

class RegistroDatos:
    def __init__(self, Building_ID: str, Item_Number: int, Description: str, Unit_Quantity: float, Stocking_Unit_of_Measure: str, Lot_Number: str, Inventory_Status: str, Storage_Location: str, Load_Number: str, FIFO_Date):
        self.Building_ID = Building_ID
        self.item = Item_Number
        self.Description = Description
        self.Unit_quantity = Unit_Quantity
        self.SUoM = Stocking_Unit_of_Measure
        self.Lot_number = Lot_Number
        self.Inventory_Status = Inventory_Status
        self.Storage_Location = Storage_Location
        self.Load_Number = Load_Number
        self.FIFO_Date = FIFO_Date

    def __str__(self):
        return f"{self.__class__.__name__}:\n{json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)}"

    def a_diccionario(self):
        return self.__dict__.copy()


class CargadorCSV:
    def __init__(self, ruta_archivo: str):
        self.ruta = ruta_archivo
        self.datos = []

    def cargar_datos(self):
        with open(self.ruta, mode="r", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo, delimiter=",")

            for fila in lector:
                # Reemplaza los espacios por guiones bajos en las llaves del diccionario
                fila_corregida = {clave.replace(" ", "_"): valor for clave, valor in fila.items()}

                # Esto saca los datos automáticamente y los asigna uno a uno
                objeto = RegistroDatos(**fila_corregida)
                self.datos.append(objeto)

        return self.datos


class FiltroReporte:
    def __init__(self, registro: list):
        self.registro = registro
        self.extracto = ()

    def filtrar_por_localidad(self, localidad: str):
        self.sloc = localidad

        for obj in self.registro:
            if obj.Storage_Location == self.sloc:
                self.extracto.append(obj)

        return self.extracto



base_datos = CargadorCSV("01 Files/Data.csv")
Localidades = FiltroReporte(base_datos.cargar_datos())
Localidades.filtrar_por_localidad("RTNTTD")