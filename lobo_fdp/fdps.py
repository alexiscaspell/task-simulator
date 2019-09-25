import math
import random
import numpy as np

#################################
# FDPs
#################################

# TPLL
lista_parametros = [544365.886143626, -42223.051395900664]
a = lista_parametros[0]
b = lista_parametros[1]


def funcion_exponencial(x):
    return (a**x) - b


fdp_tiempo_llegada = funcion_exponencial

# TPSjunior
coeficientes_fdp_junior = [
    -7.668911848103595e-55, 3.7991219649505233e-50, -8.52280055122711e-46,
    1.146009086146662e-41, -1.0303857794773394e-37, 6.543640098885148e-34,
    -3.0230293178636008e-30, 1.0310764519350724e-26, -2.608531311831282e-23,
    4.8779762211060183e-20, -6.667401231812953e-17, 6.531812779938818e-14,
    -4.4508686444895616e-11, 2.0184349389817072e-08, -5.710964340346638e-06,
    0.0009169847381366349, -0.07205256981808383, 2.092768547559989
]

fdp_tiempo_salida_junior = np.poly1d(coeficientes_fdp_junior)

# TPSsemisenior
coeficientes_fdp_semisenior = [
    7.420709583662491e-69, -4.848570292488591e-64, 1.4630139722079124e-59,
    -2.704694505351326e-55, 3.427062580313781e-51, -3.1542212645657417e-47,
    2.1804145295287186e-43, -1.1543865070415042e-39, 4.7300192847350544e-36,
    -1.5052421366962504e-32, 3.71074636256769e-29, -7.02337039985185e-26,
    1.0035754005544947e-22, -1.0519953184151934e-19, 7.686462468061054e-17,
    -3.5054417125574034e-14, 6.568761575940029e-12, 2.1053078500576667e-09,
    -1.5518941122171995e-06, 0.00035613247857040547, -0.034317864773161566,
    1.1574389356195403
]

fdp_tiempo_salida_semisenior = np.poly1d(coeficientes_fdp_semisenior)

# TPSsenior
coeficientes_fdp_senior = [
    2.207084987261066e-53, -1.1696155056116335e-48, 2.805962042078352e-44,
    -4.033620359391186e-40, 3.876257775278548e-36, -2.630829152715097e-32,
    1.29897336662051e-28, -4.73593742645359e-25, 1.2808317365317476e-21,
    -2.558848175432461e-18, 3.727155283945415e-15, -3.864905430392547e-12,
    2.7452863166714623e-09, -1.2574243515792023e-06, 0.00033800040768036985,
    -0.04607496881083196, 2.4863983927799502
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
