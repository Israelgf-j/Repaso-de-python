""""
Diseñar un sistema donde una orden procesa elementos consumibles usando diferentes estrategias de pago abstractas sin conocer los detalles de implementacion concretas.
"""

from abc import ABC, abstractmethod

def main():

    # Clase Base Abstracta, ABC
    class MetodoPago:
        @abstractmethod
        def __init__(self, monto: float):
            self.monto = monto

        # Metodo abstracto: CADA subclase DEBE implementarlo y devoler un booleano
        def procesar_pago(self):
            return False


    class PagoTarjeta(MetodoPago):
        def __init__(self, monto, numero_tarjeta: str, titular: str):
            super().__init__(monto)
            self.__numero_tarjeta = numero_tarjeta
            self.titular = titular

        def procesar_pago(self):
            print("\n\t Usted eligio: PAGO CON TARJETA\n")
            print(f"\t{self.__numero_tarjeta}")
            print(f"\t{self.titular}")

            if len(self.__numero_tarjeta) == 16:
                self.monto = (0.02 * self.monto) + self.monto             
                return True, self.monto
            else:
                return False, self.monto


    class PagoCripto(MetodoPago):
        def __init__(self, monto, wallet_addres: str):
            super().__init__(monto)
            self.__wallet_addres = wallet_addres

        def procesar_pago(self):
            print("\n\t Usted eligio: PAGO CON WALLET CRIPTO")
            return True, self.monto


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

        def mostrar_carrito(self):
            # primero le tenes que imprimir un ticket con los productos comprados:
            print(f"\t Detalles de su carrito:\n")
            for i, item in enumerate(self.lista_carrito, start=1):
                print(f"{i} ---> {item.nombre} - (${item.precio})")
        
        def calcular_total(self):
            self.total = sum(item.precio for item in self.lista_carrito)   # Aqui dice, vamos a iterar una lista que tiene objetos, "item" representa cada objeto en esa lista, y va a entrar a cada atributo tipo "precio" generando una nueva lista con esos atributos, al final solo suma esos datos de la lista.
            return self.total


    # Clase que relaciona el carrito finalizado con un metodo de pago existente
    class orden:
        def __init__(self, carrito: CarritoCompras):
            self.carrito = carrito
            
        # Obtiene el total desde el carrito, ejecuta "metodo_pago.procesar_pago()", actualiza el estado segun el resultado e imprime un recibo
        def confirmar_orden(self, metodo_pago: MetodoPago):
            self.carrito.mostrar_carrito()

            pago = metodo_pago
            estado, monto = pago.procesar_pago()

            if estado == True:
                print(f"\nMonto total: {monto}\nPago realizado EXITOSAMENTE!!!.")
            else:
                print(f"\nMonto total: {monto}\nAlgo salio mal, pago rechazado. Verifique su numero de cuenta:\n")
                


    print(f"\n\n ------------------- SU ORDEN DE COMPRA ES LA SIGUIENTE: -------------------\n")


    it1 = Producto("Coca Cola", 20)
    it2 = Producto("Azucar", 15)
    it3 = Producto("Sal", 10)
    it4 = Producto("Huevo", 100)

    carritoShein = CarritoCompras()
    carritoShein.agregar_producto(it1)
    carritoShein.agregar_producto(it2)
    carritoShein.agregar_producto(it3)
    carritoShein.agregar_producto(it4)

    pago_tar = PagoTarjeta(carritoShein.calcular_total(), "123456789abcdefg", "Juan Pezcador")
    pago_wall = PagoCripto(carritoShein.calcular_total(), "Mi_Wallet_2312")
    
    pagar = orden(carritoShein)

    # esta parte imprime todo, tomando los metodos anteriormente descritos.
    pagar.confirmar_orden(pago_wall)

    




if __name__=='__main__':
    main()