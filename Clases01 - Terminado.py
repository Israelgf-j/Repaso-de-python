"""
En este programa implementamos la creacion de 2 clases con 2 atributos:

CLASES: 
    Persona
        - nombre
        - edad
        --> Saludar
    AUTO
        - marca
        - modelo
        --> Encender
        --> Apagar

Usamos la comunicacion entre clases llamada: Composition (Has-A Relationship)
Use a composition when you want to pass an instance of one class into another class as an attribute. This keeps the class independent while allowing full data sharing

"""

def main():

    # -- Clase 01: Representa una persona que conduce ----
    class Persona:
        # El metodo constructor inicializa el estado del objeto
        def __init__(self, nombre: str, edad: int):
            self.nombre = nombre        # Atributo de nombre de la persona
            self.edad = edad            # Atributo de la edad de la persona

        # Metodo (comportamiento de la clase persona)
        def saludar(self):
            print(f'Hola, mi nombre es: {self.nombre} y tengo {self.edad} años')


    # -- Clase 02: Representa un automovil ----
    class Auto:
        def __init__(self, marca: str, modelo: str):
            self.marca = marca
            self.modelo = modelo
            self.estado_motor = False            # Estado del motor apagado

        # Este Metodo de comportamiento enciende el auto
        def Encender(self):
            if not self.estado_motor:              # Esto significa, si la variable estado_motor es FALSA
                self.estado_motor = True
                print(f'El auto: {self.marca} - {self.modelo} ha sido encendido.')
            else:
                print('El auto ya esta encendido.')

        # Este Metodo de comportamiento apaga el motor
        def Apagar(self):
            if self.estado_motor:                  # Esto significa, si la variable estado_motor es VERDADERA
                print(f'El auto: {self.marca} - {self.modelo} ha sido apagado.')
            else:
                print('El auto ya esta apagado.')


    # Creamos el ejemplo en donde una persona maneja un automovil
    # La clase conductor recibe parametros de alguien quer conduce un auto, y que clase de auto
    # Recibe parametros de clase "Persona" y "Auto"
    class Conductor:
        def __init__(self, persona_conductora: Persona):
            self.persona_conductora = persona_conductora

        def arrancar_vehiculo(self, auto: Auto):
            # Aqui accedemos al atributo nombre de la clase que se nos pasa como argumento
            print(f'{self.persona_conductora.nombre} se sube al vehiculo . . .')

            # Comunicacion: conductor le pide al objeto 'auto' que ejecute su propio método 'encender'
            auto.Encender()


    print("\n\n-------------- Ejercicio 01 --------------\n")
    # Creamos una instancia (Objeto) de la clase Persona
    personaje1 = Persona('Edwin', 28)

    # Creamos una instancia (Objeto) de la clase Auto
    auto1 = Auto('Toyota', 'Corolla')

    # Creamos una instancia (objeto) de la clase Conductor
    JonhF = Conductor(personaje1)
    JonhF.persona_conductora.saludar()
    JonhF.arrancar_vehiculo(auto1)



    """
    En este ejercicio simulamos la implementacion del uso de un cajero automatico y una tarjeta, vamos
    a utiliar la comunicacion entre clases llamada Asociacion (uso directo). 
    Un objeto recibe la referencia de otro objeto (generalmente como argumento en un método) para interactuar con él, 
    pero ninguno es dueño del otro.
    """
    class TarjetaDebito:
        def __init__(self, saldo: float):
            self.saldo = saldo
            self.nombre = "Usuario Anonimo"

        def Descontar(self, monto: float):
            self.saldo -= monto

        def Ingresar(self, monto: float):
                    self.saldo += monto


    class CajeroAutomatico:
        def __init__(self):
            pass

        def Monstrar_saldo(self, tarjeta: TarjetaDebito):
            print(f"Su saldo es de {tarjeta.saldo}")

        def Retiro(self, tarjeta: TarjetaDebito, monto: float):
            # Aqui ocurre la comunicacion entre clases, esta clase recibe como parametro un objeto y esta clase a su vez usa un metodo de este objeto.
            if tarjeta.saldo >= monto:
                tarjeta.Descontar(monto)
                print(f"Retiro exitoso, retiraste: {monto}, ahora su saldo actual es: {tarjeta.saldo}")
            else:
                print("Saldo insuficiente")

        def Ingreso(self, tarjeta: TarjetaDebito, monto: float):
            # Aqui hay otra comunicacion "Uso directo - Asociacion"
            if monto < 10000:
                tarjeta.Ingresar(monto)
                print(f"Ingreso exitoso, ingresaste: {monto}, ahora su saldo actual es: {tarjeta1.saldo}")
            else:
                print("Limite de ingreso mensual alcanzado, ingrese una cantidad menor a $ 10 000")


    print("\n\n-------------- Ejercicio 02 --------------\n")

    tarjeta1 = TarjetaDebito(100)

    cajero01 = CajeroAutomatico().Monstrar_saldo(tarjeta1)
    cajero01 = CajeroAutomatico()

    cajero01.Retiro(tarjeta1, 50)
    cajero01.Ingreso(tarjeta1, 20)
    cajero01.Ingreso(tarjeta1, 9999)
    cajero01.Ingreso(tarjeta1, 99999)


    """
    En este ejercicio simulamos la implementacion de una bateria para un aparato electronico.
    Usamos la comunicacion por COMPOSICION: Una clase crea y contiene internamente una instancia de otra clase para delegarle tareas.
    """

    print("\n\n-------------- Ejercicio 03 --------------\n")

    class Bateria:

        def nivel_carga(self):
            return "85 %"


    class Celular:
        def __init__(self, marca: str):
            self.marca = marca
            self.bateria = Bateria()        # Aqui la clase celular crea una instanciacion de la clase bateria. Crea su propia bateria.

        def Mostrar_Carga(self):
            carga = self.bateria.nivel_carga()      # Aqui la clase, realiza la comunicacion con la otra clase que hizo la instanciacion.
            print(f"El nivel de bateria actual es de: {carga}")

    
    celular01 = Celular("Nokia")
    celular01.Mostrar_Carga()
    


    print()
    print()





if __name__=='__main__':
    main()
    


