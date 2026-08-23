""""
Hacer un programa que calcule la resistencia a flexion de una viga de concreto reforzado con acero simple. Implementa el uso de clases.
"""

def main():

    class tipo_concreto:
        def __init__(self, nombre: str, resistencia: float):
            self.nombre = nombre
            self.resistencia = resistencia
            self.eps_c = 0.003  # Deformacion unitaria del concreto a la compresion

        def factor_beta1(self):
            "Esta clase esta usando unidades del sistema ingles, por lo que la resistencia a compresion se mide en psi (libras por pulgada cuadrada)"
            if self.resistencia <= 4000:   
                return 0.85
            elif self.resistencia >= 8000:
                return 0.65
            else:
                return 0.85 - ( 0.05 * (self.resistencia - 4000) / 1000)

    class Acero_corrugado:
        def __init__(self, nombre: str, fy=60000):
            self.nombre = nombre
            self.fy = fy
            self.Es = 29000000  # Modulo de elasticidad del acero en psi (libras por pulgada cuadrada)
            self.eps_tc = self.fy / self.Es  # Deformacion unitaria del acero a la tension de fluencia
            self.barras = barras = {
                "#3": {"diametro_in": 0.375, "area_in2": 0.11},
                "#4": {"diametro_in": 0.500, "area_in2": 0.20},
                "#5": {"diametro_in": 0.625, "area_in2": 0.31},
                "#6": {"diametro_in": 0.750, "area_in2": 0.44},
                "#7": {"diametro_in": 0.875, "area_in2": 0.60},
                "#8": {"diametro_in": 1.000, "area_in2": 0.79},
                "#9": {"diametro_in": 1.128, "area_in2": 1.00},
                "#10": {"diametro_in": 1.270, "area_in2": 1.27},
                "#11": {"diametro_in": 1.410, "area_in2": 1.56},
            }

    class seccion:
        def __init__(self, ancho: float, altura: float, recubrimiento: float):
            self.bw = ancho
            self.h = altura
            self.r = recubrimiento
            self.d = self.h - self.r  # Altura efectiva de la seccion

    class viga:
        def __init__(self, seccion: seccion, concreto: tipo_concreto, acero: Acero_corrugado, barra: str, num_barras: int, longitud_viga: float):
            self.seccion = seccion
            self.concreto = concreto
            self.acero = acero
            self.barra = barra
            self.num_barras = num_barras
            self.As = self.num_barras * self.acero.barras[self.barra]["area_in2"]  # Area de acero de refuerzo
            self.longitud_viga = longitud_viga

            # Cuantia de acero de la seccion de la viga
            self.ro = self.As / (self.seccion.bw * self.seccion.d)

            # Cuantia de acero balanceada
            self.ro_b = 0.85 * self.concreto.factor_beta1() * (self.concreto.resistencia / self.acero.fy) * ( 87000 / (87000 + self.acero.fy) ) * (self.seccion.d)

            # Cuantia de acero maxima
            self.ro_max = (( (0.003 + (self.acero.fy / self.acero.Es)) ) / ( (0.006 + (self.acero.fy / self.acero.Es)) )) * self.ro_b 

            # Cuantia de acero minima
            if self.concreto.resistencia < 4500:
                self.ro_min = 200 / self.acero.fy
            else:
                self.ro_min = (3 / self.acero.fy) * (self.concreto.resistencia ** 0.5)

            # profundidad del bloque de compresion
            self.a = (self.As * self.acero.fy) / (self.concreto.factor_beta1() * self.concreto.resistencia * self.seccion.bw)

            # profundidad del eje neutro
            self.c = self.a / self.concreto.factor_beta1()

            # Deformacion unitaria del acero a la tension
            self.eps_t = 0.003 * ((self.seccion.d - self.c) / self.c)

            # Factor RU para simplificar el calculo de la resistencia a flexion
            self.RU = self.ro * self.acero.fy * (1 - (self.ro * self.acero.fy) / (1.7 * self.concreto.resistencia))

        def revision_aceros(self):
            print(f"\n\n----------- Revision de cuantia de acero: -----------\n")
            print(f"Cuantia de acero de la seccion: {self.ro:.4f}")
            print(f"Cuantia de acero minima: {self.ro_min:.4f}")
            print(f"Cuantia de acero maxima: {self.ro_max:.4f}")
            print(f"Cuantia de acero balanceada: {self.ro_b:.4f}")

            if (self.ro > self.ro_min) and (self.ro < self.ro_max):
                print("\n\nLa cuantia de acero cumple\n")
            else:
                print("\n\nRevisar la cuantia de acero, no cumple con los limites establecidos por el ACI 318-19\n")

        def factor_reduccion(self):
            print(f"\n\n----------- Factor de reduccion de resistencia a flexion: -----------\n")
            if self.eps_t < self.acero.eps_tc:
                print("La deformacion unitaria del acero es menor a la deformacion unitaria del acero a la tension de fluencia, por lo que la viga es frágil y no cumple con los requisitos del ACI 318-19")
                return 0.65
            elif self.eps_t > self.acero.eps_tc + 0.003:
                print("La deformacion unitaria del acero es mayor a la deformacion unitaria del acero a la tension de fluencia, por lo que la viga es dúctil y cumple con los requisitos del ACI 318-19")
                return 0.90
            else:
                print("La deformacion de la seccion se encuentra en la zona de transicion, por lo que debe ajustarse el factor de reduccion de resistencia a flexion, segun el ACI 318-19")
                return 0.65 + ( (self.ro_b - self.ro) / (2 * self.ro) )

        def resistencia_flexion(self):
            phi = self.factor_reduccion()
            Mn = self.RU * self.seccion.bw * self.seccion.d ** 2
            print(f"\n\n----------- Resistencia nominal a flexion: -----------\n")
            print(f"Factor de reduccion: {phi:.2f}")
            print(f"Resistencia nominal a flexion: {Mn:.2f} lb-in")
            print(f"Resistencia nominal a flexion: {Mn/12000:.2f} kip-ft")

            return phi * Mn

        def detalles(self):
            print(f"\n\n----------- Detalles de la viga: -----------\n")
            print(f"Seccion: {self.seccion.bw} in x {self.seccion.h} in")
            print(f"Recubrimiento: {self.seccion.r} in")
            print(f"Altura efectiva: {self.seccion.d} in")

            print(f"\n\n----------- Propiedades del concreto y acero: -----------\n")
            print(f"Concreto: {self.concreto.nombre} con resistencia a compresion de {self.concreto.resistencia} psi")
            print(f"Acero: {self.acero.nombre} con fy de {self.acero.fy} psi")
            print(f"Area de acero (As): {self.As} in2")
            print(f"Barras: {self.num_barras} barras del {self.barra}")
            print(f"Longitud de la viga (L): {self.longitud_viga} ft")
            print(f"Profundidad del bloque de compresion (a): {self.a:.2f} in")
            print(f"Profundidad del eje neutro (c): {self.c:.2f} in")
            print(f"Deformacion unitaria del acero a la tension (eps_t): {self.eps_t:.5f}")
            print(f"Factor RU: {self.RU:.2f}")

            




        

    # Creamos los elementos para el calculo de la resistencia a flexion
    seccion1 = seccion(ancho=12, altura=23.5, recubrimiento=2.5)
    concreto1 = tipo_concreto(nombre="Concreto normal", resistencia=3000)
    acero1 = Acero_corrugado(nombre="Acero #9", fy=60000)
    viga1 = viga(seccion=seccion1, concreto=concreto1, acero=acero1, barra="#9", num_barras=3, longitud_viga=20)
    viga1.detalles()
    viga1.revision_aceros()
    viga1.resistencia_flexion()




if __name__=='__main__':
    main()