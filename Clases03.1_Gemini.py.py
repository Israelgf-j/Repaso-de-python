from abc import ABC, abstractmethod

# 1. Clase Base Abstracta (Hereda de ABC)
class MetodoPago(ABC):
    
    @abstractmethod
    def procesar_pago(self, monto: float) -> bool:
        """Método obligatorio que debe devolver True si el pago fue exitoso."""
        pass


# 2. Subclases con Polimorfismo
class PagoTarjeta(MetodoPago):
    def __init__(self, numero_tarjeta: str, titular: str):
        self.__numero_tarjeta = numero_tarjeta
        self.titular = titular

    def procesar_pago(self, monto: float) -> bool:
        print("\n\tUsted eligió: PAGO CON TARJETA")
        if len(self.__numero_tarjeta) == 16:
            monto_final = monto * 1.02  # Comisión del 2%
            print(f"\tCobro procesado a {self.titular}. Total con comisión: ${monto_final:.2f}")
            return True
        else:
            print("\tNúmero de tarjeta inválido.")
            return False


class PagoCripto(MetodoPago):
    def __init__(self, wallet_address: str):
        self.__wallet_address = wallet_address

    def procesar_pago(self, monto: float) -> bool:
        print("\n\tUsted eligió: PAGO CON WALLET CRIPTO")
        print(f"\tTransferencia de ${monto:.2f} a la wallet {self.__wallet_address}")
        return True


# 3. Entidades y Gestores
class Producto:
    def __init__(self, nombre: str, precio: float):
        self.nombre = nombre
        self.precio = precio


class CarritoCompras:
    def __init__(self):
        self.lista_carrito: list[Producto] = []

    def agregar_producto(self, producto: Producto):
        self.lista_carrito.append(producto)

    def mostrar_carrito(self):
        print("\tDetalles de su carrito:\n")
        for i, item in enumerate(self.lista_carrito, start=1):
            print(f"\t{i}. {item.nombre} - (${item.precio:.2f})")

    def calcular_total(self) -> float:
        return sum(item.precio for item in self.lista_carrito)


# 4. Clase Orquestadora
class Orden:
    def __init__(self, carrito: CarritoCompras):
        self.carrito = carrito
        self.estado = "Pendiente"

    def confirmar_orden(self, metodo_pago: MetodoPago):
        self.carrito.mostrar_carrito()
        total = self.carrito.calcular_total()

        # Delegación: El método de pago procesa el total dinámicamente
        pago_exitoso = metodo_pago.procesar_pago(total)

        if pago_exitoso:
            self.estado = "Completada"
            print(f"\nEstado de Orden: {self.estado} | ¡Pago realizado con éxito!")
        else:
            self.estado = "Rechazada"
            print(f"\nEstado de Orden: {self.estado} | El pago no pudo ser procesado.")


# --- Ejecución ---
def main():
    it1 = Producto("Coca Cola", 20)
    it2 = Producto("Azúcar", 15)
    it3 = Producto("Sal", 10)
    it4 = Producto("Huevo", 100)

    carrito = CarritoCompras()
    carrito.agregar_producto(it1)
    carrito.agregar_producto(it2)
    carrito.agregar_producto(it3)
    carrito.agregar_producto(it4)

    # Las estrategias de pago se configuran con sus datos, no con el monto fijo
    pago_tarjeta = PagoTarjeta("1234567890123456", "Juan Pescador")
    pago_cripto = PagoCripto("Mi_Wallet_2312")

    print("------------------- ORDEN DE COMPRA -------------------")
    orden_actual = Orden(carrito)
    orden_actual.confirmar_orden(pago_tarjeta)


if __name__ == '__main__':
    main()