import csv
from dataclasses import dataclass, asdict



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

        """
        def filtrar_registros(self, storage_location: str = None, id_producto: str = None, estado: str = None):
    # Comenzamos con todos los registros disponibles
    resultados = self.registro
    
    # 1. Filtro por Storage Location (con soporte para '%')
    if storage_location:
        busqueda_sl = storage_location.strip().upper()
        if busqueda_sl.endswith('%'):
            texto_base = busqueda_sl[:-1]
            resultados = [r for r in resultados if r.Storage_Location.upper().startswith(texto_base)]
        else:
            resultados = [r for r in resultados if r.Storage_Location.upper() == busqueda_sl]
            
    # 2. Filtro por ID de Producto (Búsqueda exacta)
    if id_producto:
        busqueda_id = id_producto.strip()
        resultados = [r for r in resultados if r.ID_Producto == busqueda_id]
        
    # 3. Filtro por Estado (Búsqueda exacta)
    if estado:
        busqueda_est = estado.strip().upper()
        resultados = [r for r in resultados if r.Estado.upper() == busqueda_est]
        
    return resultados

        """


    


    def filtrar_por_item(self, item: int):
        return [
            registro
            for registro in self.registro
            if registro.Item_Number == item
        ]


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


# Aplicamos los filtros por localidad
filtro_sloc = base_datos.filtrar_por_storage_location("RTN%")

for registro in filtro_sloc:
    print(registro)

print(len(filtro_sloc))

# Aplicamos los filtros por item
#filtro_item = base_datos.filtrar_por_item(21290744)
#print(len(filtro_item))



#for registro in filtro_item:
#    print(registro)

#archivo = ExportarCSV()
#archivo.exportar_csv(filtro_item)

