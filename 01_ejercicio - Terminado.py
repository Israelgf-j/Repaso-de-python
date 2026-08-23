def main():
    """
    Creamos un sistema de facuturacion, que nos ayude a calcular una cuenta final con detalles de precios por productos tomados.
    """

    # Clase producto, que contiene el nombre y precio del producto, usada para crear una lista de productos que se van a facturar.
    class Producto:
        def __init__(self, nombre: str, precio: float):
            self.nombre = nombre
            self.precio = precio

    # Clase cliente, que contiene el nombre y email del cliente, usada para crear una factura con los datos del cliente.
    class Cliente:
        def __init__(self, nombre_cliente: str, email: str):
            self.nombre_cliente = nombre_cliente
            self.email = email

    # Clase factura, que contiene el cliente y la lista de productos, usada para gestionar la facturacion.
    class Factura:
        def __init__(self, cliente: Cliente):
            self.cliente = cliente
            self.lista_productos = []

        def agregar_producto(self, producto: Producto):
            self.lista_productos.append(producto)

        def calcular_total(self):
            total = sum(producto.precio for producto in self.lista_productos)
            return total

        def mostrar_detalles(self):
            print(f"Factura para: {self.cliente.nombre_cliente} con direccion email: ({self.cliente.email})")
            print("Productos:")
            for producto in self.lista_productos:
                print(f"- {producto.nombre}: ${producto.precio:.2f}")
            print(f"Total: ${self.calcular_total():.2f}")

    cliente01 = Cliente("Juan Perez", "juanitocarmelo@gmail.com")
    factura01 = Factura(cliente01)

    producto01 = Producto("Laptop", 1200.00)
    producto02 = Producto("Mouse", 25.00)
    producto03 = Producto("Teclado", 75.00)

    factura01.agregar_producto(producto01)
    factura01.agregar_producto(producto02)
    factura01.agregar_producto(producto03)

    factura01.mostrar_detalles()
    factura01.calcular_total()




if __name__=='__main__':
    main()