"Hacemos un repaso del uso de la herencia en python"

def main():

    # -------------------------------------------------------------------------------------------
    # Clase padre o superclase
    class Vehiculo:
        def __init__(self, marca: str, anio: str):
            # Atributos de la clase Vehiculo
            self.marca = marca
            self.anio = anio

        def mostrar_info(self):
            # Metodo que muestra la información del vehículo
            return f"Marca: {self.marca}, Año: {self.anio}"


    # Clase hija o subclase, que hereda de Vehiculo sus atributos y métodos
    class Auto(Vehiculo):
        # Atributos de la clase Auto y adicional, agrega un nuevo atributo 'puertas'
        def __init__(self, marca, anio, puertas: int):
            super().__init__(marca, anio)  # Hereda los atributos de Vehiculo
            self.puertas = puertas

        def mostrar_info(self):
            # Puedes usar el método del padre y agregar más detalles
            info_base = super().mostrar_info()
            return f"{info_base}, Puertas: {self.puertas}"


    # Clase hija o subclase, que hereda de Vehiculo sus atributos y métodos
    class Moto(Vehiculo):
        def __init__(self, marca, anio, tiene_casco: bool):
            super().__init__(marca, anio)
            self.tiene_casco = tiene_casco

        def mostrar_info(self):
            info_base = super().mostrar_info()
            return f"{info_base}, Tiene casco: {'Sí' if self.tiene_casco else 'No'}"

    # Prueba tu código creando un objeto
    print("\n\n-------------- Ejercicio 01 --------------\n")
    mi_auto = Auto("Toyota", "2024", 4)
    print(mi_auto.mostrar_info())

    mi_moto = Moto("Italika", "2026", True)
    print(mi_moto.mostrar_info())



    # -------------------------------------------------------------------------------------------
    print("\n\n-------------- Ejercicio 02 --------------\n")


    # Clase Padre
    class Empleado:
        def __init__(self, nombre: str, id_empleado: str, sueldo_base: float):
            self.nombre = nombre
            self.id_empleado = id_empleado
            self.sueldo_base = sueldo_base

        def calcular_sueldo(self):
            # Este método será sobrescrito por las clases hijas (a esto se le llamna polimorfismo)
            return self.sueldo_base

        def mostrar_detalle(self):
            return f"ID: {self.id_empleado} | {self.nombre} | Sueldo Final: ${self.calcular_sueldo():.2f}"


    # --- TU TRABAJO EMPIEZA AQUÍ ---

    # 1. Clase Hija: Empleado con comisión (Vendedor)
    class EmpleadoComision(Empleado):
        def __init__(self, nombre, id_empleado, sueldo_base, ventas_realizadas: int, comision_por_venta: float):
            # TODO: Usa super() para heredar los atributos del padre
            super().__init__(nombre, id_empleado, sueldo_base)
            # TODO: Guarda los nuevos atributos específicos del vendedor
            self.ventas_realizadas = ventas_realizadas
            self.comision_por_venta = comision_por_venta


        def calcular_sueldo(self):
            # TODO: Sobrescribe el método. El sueldo es: sueldo_base + (ventas * comision)
            self.sueldo_base = self.sueldo_base + (self.ventas_realizadas * self.comision_por_venta)
            return self.sueldo_base


    # 2. Clase Hija: Empleado por horas (Freelancer)
    class EmpleadoHoras(Empleado):
        def __init__(self, nombre, id_empleado, sueldo_base, pago_por_hora: float, horas_trabajadas: float):
            # TODO: Aquí el sueldo_base del padre puede ser 0, ya que gana por hora.
            # TODO: Usa super() e inicializa los atributos de horas.
            super().__init__(nombre, id_empleado, sueldo_base)
            self.sueldo_base = 0
            self.pago_por_hora = pago_por_hora
            self.horas_trabajadas = horas_trabajadas


        def calcular_sueldo(self):
            # TODO: Sobrescribe el método. El sueldo es: horas_trabajadas * pago_por_hora
            self.sueldo_base = self.horas_trabajadas * self.pago_por_hora + self.sueldo_base
            return self.sueldo_base


    # --- CÓDIGO DE PRUEBA (Descoméntalo cuando termines las clases) ---
    vendedor = EmpleadoComision("Ana Gómez", "V001", 1500, 10, 50)
    freelancer = EmpleadoHoras("Carlos Ruiz", "H002", 1000, 25, 40) # 25 dólares la hora, 40 horas

    print(vendedor.mostrar_detalle())  # Debería dar un sueldo de 2000
    print(freelancer.mostrar_detalle()) # Debería dar un sueldo de 1000

    print()
    print()





if __name__ == "__main__":
    main()
