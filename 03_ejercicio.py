class Canal:
    def __init__(self, tirante: float, base:float):
        self.y = tirante
        self.b = base

    def area(self):     # if self.edad is not None else "una edad desconocida"
        return f"\n\t-- {self.y} de tirante\n\t-- {self.b} de base" if self.b is not None else f"\n\t-- {self.y} de tirante\n\t-- No tiene base"

# Esta clase hija hereda ambos atributos de la clase padre, por eso usamos super() para heredar todo completo
class Cuadrado(Canal):
    def __init__(self, tirante: float, base: float):
        super().__init__(tirante, base)

    def area(self):
        A = self.y * self.b
        datos_entrada = super().area()
        return f"\n-- El canal RECTANGULAR tiene un área mojada de: \n\t{A} unidades cuadradas \n\n\ty los datos del canal son: {datos_entrada}\n\n"


class Triangulo(Canal):
    def __init__(self, tirante: float, talud: int):
        super().__init__(tirante, base=None)
        self.z = talud

    def area(self):

        A = self.z * self.y ** 2

        datos_entrada = super().area()
        return f"\n-- El canal TRIANGULAR tiene un área mojada de: \n\t{A} unidades cuadradas \n\n\ty los datos del canal son: {datos_entrada}\n\t-- {self.z} de talud\n\n"


class Trapecio(Canal):
    def __init__(self, tirante:float, base:float, talud: int):
        super().__init__(tirante, base)
        self.z = talud

    def area(self):

        A = (self.b + self.z * self.y) * self.y

        datos_entrada = super().area()
        return f"\n-- El canal TRAPEZOIDAL tiene un área mojada de: \n\t{A} unidades cuadradas \n\n\ty los datos del canal son: {datos_entrada}\n\t-- {self.z} de talud\n\n"




print("\n\n-------------- Propiedades basicas de los canales --------------\n")

# inciamos una instancia de la clase Cuadrado, que hereda de la clase Canal sus atributos y métodos
# Ya teniamos todo el programa hecho y no funcionaba debido a que no habiamos escrito de manera correcta los metodos constructor de las clases, escribiamos "_init_" y no "__init__" y eso hacia que no se ejecutara el programa, ya que no se estaba llamando al metodo constructor de la clase padre.
# No escribiamos la cantidad adecuada de guiones bajos.

canal_rectangular = Cuadrado(3, 5)
print(canal_rectangular.area())

canal_triangular = Triangulo(3, 2)
print(canal_triangular.area())

canal_trapezoidal = Trapecio(3, 6, 2)
print(canal_trapezoidal.area())

