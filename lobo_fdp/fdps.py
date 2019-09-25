import math
import random
import numpy as np

#################################
# FDPs
#################################

# TPLL
lista_parametros = [4878.173486783057, -261.0054954271899]
a = lista_parametros[0]
b = lista_parametros[1]


def funcion_exponencial(x):
    return (a**x) - b


fdp_tiempo_llegada = funcion_exponencial

# TPSjunior
coeficientes_fdp_junior = [
    -4.530670610548935e-51, 1.3466763400141573e-46, -1.8126483896359927e-42,
    1.462414739398922e-38, -7.889211539716545e-35, 3.006106761647825e-31,
    -8.332562979407425e-28, 1.7052119385473823e-24, -2.5884203213028863e-21,
    2.9042210964327665e-18, -2.3817591277338227e-15, 1.3999941657962151e-12,
    -5.723853709477318e-10, 1.5574343664982318e-07, -2.6439649723827035e-05,
    0.002547179828157319, -0.12008761636347302, 2.092768547559989
]

fdp_tiempo_salida_junior = np.poly1d(coeficientes_fdp_junior)

# TPSsemisenior
coeficientes_fdp_semisenior = [
    3.3827443500755714e-64, -1.326137904572065e-59, 2.400903565080804e-55,
    -2.66315051135942e-51, 2.02465382582005e-47, -1.11807812103646e-43,
    4.637354660517201e-40, -1.4731051117030044e-36, 3.621568102690832e-33,
    -6.914986913492908e-30, 1.0228160072411649e-26, -1.1615370550060663e-23,
    9.958381365686125e-21, -6.263308508701941e-18, 2.745792776942229e-15,
    -7.513378156201473e-13, 8.447481450539976e-11, 1.624465933686475e-08,
    -7.184694963968665e-06, 0.0009892568849177912, -0.05719644128860249,
    1.1574389356195403
]

fdp_tiempo_salida_semisenior = np.poly1d(coeficientes_fdp_semisenior)

# TPSsenior
coeficientes_fdp_senior = [
    7.823463316434047e-50, -2.4875645628419225e-45, 3.5806699075369563e-41,
    -3.0883660197917515e-37, 1.7807282387275628e-33, -7.251517368197993e-30,
    2.1482644555205725e-26, -4.6994247757161914e-23, 7.625741458355654e-20,
    -9.140832816902664e-17, 7.988587285548304e-14, -4.97030019340605e-11,
    2.1182764789131657e-08, -5.821409035088905e-06, 0.0009388900213343603,
    -0.07679161468471989, 2.4863983927799502
]

fdp_tiempo_salida_senior = np.poly1d(coeficientes_fdp_senior)

#################################
# FUNCIONES
#################################


def metodo_del_rechazo(a: int, b: int, h: int, funcion) -> int:

    while True:
        x = ((b - a) * random.random()) + a
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
    return metodo_del_rechazo(a=0,
                              b=4260,
                              h=1,
                              funcion=fdp_tiempo_salida_junior)


def obtener_tiempo_resolucion_semisenior() -> int:
    return metodo_del_rechazo(a=0,
                              b=4260,
                              h=1,
                              funcion=fdp_tiempo_salida_semisenior)


def obtener_tiempo_resolucion_senior() -> int:
    return metodo_del_rechazo(a=0,
                              b=4260,
                              h=1,
                              funcion=fdp_tiempo_salida_senior)


if __name__ == "__main__":

    cantidad_puntos = 100

    print(
        f"LLEGADAS \n{[obtener_intervalo_arribo() for i in range(cantidad_puntos)]} \n"
    )
    print(
        f"SALIDAS JUNIOR \n {[obtener_tiempo_resolucion_junior() for i in range(cantidad_puntos)]} \n\n"
    )
    print(
        f"SALIDAS SEMISENIOR \n {[obtener_tiempo_resolucion_semisenior() for i in range(cantidad_puntos)]} \n\n"
    )
    print(
        f"SALIDAS SENIOR \n {[obtener_tiempo_resolucion_senior() for i in range(cantidad_puntos)]} \n\n"
    )
