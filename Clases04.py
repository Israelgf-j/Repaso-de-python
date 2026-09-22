# Aqui estamos dominando GETTERS y SETTERS

class Nodo1:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def cambiar_x(self, x):
        if x < 0:
            raise ValueError("X no puede ser negativa:")
        self.x = x



# Aqui recibimos cualquier parametro para instanciar la clase, no hay restricciones para que recibir.
nodo = Nodo1(2, 3)

print(f"-----------------------------\n")
print("X vale:", nodo.x)

nodo.x = 5

print("Ahora X vale:",nodo.x)
# Como ves, podemos modificar el valor de la componente x sin restriccion, sin importar.

print(f"-----------------------------\n")
nodo.cambiar_x(10)
print("Ahora X vale:", nodo.x)

# Si te fijas hacemos la validacion con un metodo extra en la clase, podemos hacer algo mas elegante y simplificado de la siguiente manera:
# Aqui hacemos una validacion por la parte trasera de python, hace la validacion en automatico  

class Nodo2:

    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, valor):
        if valor < 0:
            raise ValueError("X no puede ser negativa:", valor)

        self._x = valor


print(f"\n\n\t-----------------------------\n")
nodo2 = Nodo2(2)
print(nodo2.x)

nodo2 = Nodo2(3)

print(f"\n\n\t-----------------------------\n")

class Material:

    def __init__(self, E):
        self.E = E

    @property
    def E(self):
        return self._E

    @E.setter
    def E(self, valor):
        if valor <= 0:
            raise ValueError("E debe ser mayor que cero.", valor)

        self._E = valor

# Definimos la clase material y hacemos una validacion para que este modulo de elasticidad sea mayor a cero.
print(f"\n\t-----------------------------\n")
acero = Material(200)
print("Modulo de elasticidad:",acero.E)

# Aqui la propiedad funcina como una puerta de entrada, y causa un error
acero.E = 500


class Barra:

    def __init__(self, nodo_i, nodo_j):
        self.nodo_i = nodo_i
        self.nodo_j = nodo_j

    # Al agregar property a un metodo, este se convierte en una propiedad de la clase Barra, no en un metodo:
    @property
    def longitud(self):
        dx = self.nodo_j.x - self.nodo_i.x
        dy = self.nodo_j.y - self.nodo_j.y

        return ( dx**2 + dy**2 ) ** (0.5)


n1 = Nodo1(0, 0)
n2 = Nodo1(3, 4)

# Aqui la longitud de la barra es una propiedad, no un metodo.
barra1 = Barra(n1, n2)
L = barra1.longitud

print(f"\n\t-----------------------------\n")
print("Longitud de la barra:",L)