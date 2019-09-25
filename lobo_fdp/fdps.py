import math
import random
import numpy as np

#################################
# FDPs
#################################

# TPLL
a = 1936.2424
b = -92.27092485
def funcion_exponencial(x):
    return (a**x) - b

fdp_tiempo_llegada = funcion_exponencial


# TPSjunior
coeficientes_fdp_junior = [-2.4600390113209675e-40, 6.362883152324875e-36, -7.164448509800597e-32, 4.617719233733805e-28, -1.8856484247955166e-24, 5.104026377575573e-21, -
                           9.318900302794241e-18, 1.1466601276145397e-14, -9.349083972457706e-12, 4.877430614443861e-09, -1.535271761042662e-06, 0.00026555569628266705, -0.021596129003579365, 0.6709690263283213]

fdp_tiempo_salida_junior = np.poly1d(coeficientes_fdp_junior)


# TPSsemisenior
coeficientes_fdp_semisenior = [1.7218943104357503e-42, -4.3696602417465295e-38, 4.911189982540232e-34, -3.226359519882515e-30, 1.3771266591828776e-26, -4.016114654160919e-23, 8.192499558186388e-20, -
                               1.176721210895765e-16, 1.1817657017333128e-13, -8.127784196562722e-11, 3.687992821932516e-08, -1.0401689992807276e-05, 0.0016637239381206794, -0.13015931884056967, 3.703540154817717]


fdp_tiempo_salida_semisenior = np.poly1d(coeficientes_fdp_semisenior)


# TPSsenior
coeficientes_fdp_senior = [8.552966751209871e-34, -1.7771653754317544e-29, 1.578405120357886e-25, -7.8535205246181315e-22, 2.4131505284736885e-18, -4.765617397366948e-15,
                           6.109379234711605e-12, -5.02016443809706e-09, 2.5479027875340355e-06, -0.0007432372167971258, 0.10880124255410058, -5.76034315597245]

fdp_tiempo_salida_senior = np.poly1d(coeficientes_fdp_senior)


#################################
# FUNCIONES
#################################

def metodo_del_rechazo(a: int, b: int, h: int, funcion) -> int:

    while True:
        x = ((b-a) * random.random()) + a
        y = h * random.random()

        if y <= funcion(x):
            return int(x)


def obtener_intervalo_arribo(tipo_tarea: str = "") -> int:
    return int(fdp_tiempo_llegada(random.random()))


def obtener_tiempo_resolucion(perfil: str, tipo_tarea: str) -> int:
    if perfil == "junior":
        return obtener_tiempo_resolucion_junior()
    elif perfil == "semisenior":
        return obtener_tiempo_resolucion_semisenior()
    elif perfil == "senior":
        return obtener_tiempo_resolucion_senior()


def obtener_tiempo_resolucion_junior() -> int:
    return metodo_del_rechazo(a=0, b=4260, h=1, funcion=fdp_tiempo_salida_junior)


def obtener_tiempo_resolucion_semisenior() -> int:
    return metodo_del_rechazo(a=0, b=4260, h=1, funcion=fdp_tiempo_salida_semisenior)


def obtener_tiempo_resolucion_senior() -> int:
    return metodo_del_rechazo(a=0, b=4260, h=1, funcion=fdp_tiempo_salida_senior)


if __name__ == "__main__":

    cantidad_puntos = 100

    print(
        f"LLEGADAS \n{[obtener_intervalo_arribo() for i in range(cantidad_puntos)]} \n")
    print(
        f"SALIDAS JUNIOR \n {[obtener_tiempo_resolucion_junior() for i in range(cantidad_puntos)]} \n\n")
    print(
        f"SALIDAS SEMISENIOR \n {[obtener_tiempo_resolucion_semisenior() for i in range(cantidad_puntos)]} \n\n")
    print(
        f"SALIDAS SENIOR \n {[obtener_tiempo_resolucion_senior() for i in range(cantidad_puntos)]} \n\n")
