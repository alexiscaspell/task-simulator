import math
import random
import numpy as np
import json

#################################
# CONFIGURACION
#################################
RUTA_CONFIG_SALIDA = "./config/fdp_config.json"
coeficientes = json.load(open(RUTA_CONFIG_SALIDA))



#################################
# FDPs
#################################

# TPLL
def fdp_tiempo_llegada(x):
    a = coeficientes["llegadas"][0]
    b = coeficientes["llegadas"][1]
    return a*x + b


# TPSjunior
def fdp_tiempo_salidas_junior(x):
    a = coeficientes["salidas_junior"][0]
    b = coeficientes["salidas_junior"][1]
    return a**x - b


# TPSsemisenior
def fdp_tiempo_salida_semisenior(x):
    a = coeficientes["salidas_semisenior"][0]
    b = coeficientes["salidas_semisenior"][1]
    return a**x - b

# TPSsenior
def fdp_tiempo_salida_senior(x):
    a = coeficientes["salidas_senior"][0]
    b = coeficientes["salidas_senior"][1]
    return a**x - b

#################################
# FUNCIONES
#################################

def obtener_intervalo_arribo(tipo_tarea: str = "") -> int:

    fdp = 0
    fdp = fdp if fdp > 0 else fdp_tiempo_llegada(random.random())

    return int(fdp)


def obtener_tiempo_resolucion(perfil: str, tipo_tarea: str = "") -> int:

    rnd = random.random()

    if perfil == "junior":
        fdp = fdp_tiempo_salidas_junior(rnd)
    elif perfil == "semisenior":
        fdp = fdp_tiempo_salida_semisenior(rnd)
    elif perfil == "senior":
        fdp = fdp_tiempo_salida_senior(rnd)

    return int(fdp)


if __name__ == "__main__":

    cantidad_puntos = 100

    print(
        f"LLEGADAS \n{[obtener_intervalo_arribo() for i in range(cantidad_puntos)]} \n"
    )
    print(
        f"SALIDAS JUNIOR \n {[obtener_tiempo_resolucion(perfil='junior') for i in range(cantidad_puntos)]} \n\n"
    )
    print(
        f"SALIDAS SEMISENIOR \n {[obtener_tiempo_resolucion(perfil='semisenior') for i in range(cantidad_puntos)]} \n\n"
    )
    print(
        f"SALIDAS SENIOR \n {[obtener_tiempo_resolucion(perfil='senior') for i in range(cantidad_puntos)]} \n\n"
    )
