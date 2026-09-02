""""
Diseñar un sistema donde una orden procesa elementos consumibles usando diferentes estrategias de pago abstractas sin conocer los detalles de implementacion concretas.
"""

def main():

    # Clase Base Abstracta, ABC
    class MetodoPago:
        def __init__(self, monto: float):
            self.monto = monto

        # Metodo abstracto: CADA subclase DEBE implementarlo y devoler un booleano
        def procesar_pago(self):
            return False


    class PagoTarjeta(MetodoPago):
        def __init__(self, monto, numero_tarjeta: str, titular: str):
            super().__init__(monto)
            self.numero_tarjeta = numero_tarjeta
            self.titular = titular

        def procesar_pago(self):
            if len(self.numero_tarjeta) == 16:
                self.monto = (- 0.02 * self.monto) + self.monto
                print(f"\n\nPago realizado EXITOSAMENTE!!!. \nMonto total: {self.monto}")
                return True
            else:
                print("\n\nPago Rechazado. Verifique su numero de cuenta\n")
                print(f"{len(self.numero_tarjeta)}")
                return False

    class PagoCripto(MetodoPago):
        def __init__(self, monto, wallet_addres: str):
            super().__init__(monto)
            self.__wallet_addres = wallet_addres

        def procesar_pago(self):
            print(f"\n\nPago realizado EXITOSAMENTE!!!. \nMonto total: {self.monto}")
            return True


    # Clase Base Abstracta, ABC: Representa un item individual disponible en la tienda.
    class Producto:
        def __init__(self, nombre: str, precio:float):
            self.nombre = nombre
            self.precio = precio

        def obtener_precio(self):
            return self.precio

    # Clase que gestiona los productos que el usuario elige
    class CarritoCompras:
        def __init__(self):
            self.lista_carrito = []

        def agregar_producto(self, producto: Producto):
            self.lista_carrito.append(producto)
        
        def calcular_total(self):
            self.total = sum(item.precio for item in self.lista_carrito)   # Aqui dice, vamos a iterar una lista que tiene objetos, "item" representa cada objeto en esa lista, y va a entrar a cada atributo tipo "precio" generando una nueva lista con esos atributos, al final solo suma esos datos de la lista.
            return self.total

    # Clase que relaciona el carrito finalizado con un metodo de pago existente
    class orden:
        def __init__(self, carrito: CarritoCompras, estado: str):
            self.carrito = carrito
            self.estado = estado

        # Obtiene el total desde el carrito, ejecuta "metodo_pago.procesar_pago()", actualiza el estado segun el resultado e imprime un recibo
        def confirmar_orden(self, forma_pago: MetodoPago):
            # primero le tenes que imprimir un ticket con los productos comprados:
            print(f"\n\n ------------ Su carrito es el siguiente: ------------\n")
            i = 0
            for item in self.carrito.lista_carrito():
                print(f"{i+1}) --> {item}")
            

            self.forma_pago = forma_pago


    print(f"\n\n -------------- Le comparto su orden de compra: --------------\n")


    it1 = Producto("Coca Cola", 20)
    it2 = Producto("Azucar", 15)
    it3 = Producto("Sal", 10)
    it4 = Producto("Huevo", 100)

    carritoShein = CarritoCompras()
    carritoShein.agregar_producto(it1)
    carritoShein.agregar_producto(it2)
    carritoShein.agregar_producto(it3)
    carritoShein.agregar_producto(it4)

    # Si imprime total = 145 y el tipo de valor: int
    #print(carritoShein.calcular_total())
    #rint(type(carritoShein.calcular_total()))
    
    pagar_cuenta = MetodoPago(carritoShein.calcular_total())
    pago_con_tarjeta = PagoTarjeta(pagar_cuenta, "abcd1234efgh5678", "Juan Pescador")

    

    se_pago = pago_con_tarjeta.procesar_pago()

    cuenta1 = orden(carritoShein, se_pago)



    
        






if __name__=='__main__':
    main()