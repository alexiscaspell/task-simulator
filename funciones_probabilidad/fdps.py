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
lista_parametros = coeficientes["llegadas"]
a = lista_parametros[0]
b = lista_parametros[1]

def funcion_exponencial(x):
    return a*x + b

fdp_tiempo_llegada = funcion_exponencial

# TPSjunior
fdp_tiempo_salida_junior = np.poly1d(coeficientes["salidas_junior"])

# TPSsemisenior
fdp_tiempo_salida_semisenior = np.poly1d(coeficientes["salidas_semisenior"])

# TPSsenior
fdp_tiempo_salida_senior = np.poly1d(coeficientes["salidas_senior"])

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
                              b=coeficientes["maximo_x_junior"],
                              h=coeficientes["maximo_y_junior"],
                              funcion=fdp_tiempo_salida_junior)


def obtener_tiempo_resolucion_semisenior() -> int:
    return metodo_del_rechazo(a=0,
                              b=coeficientes["maximo_x_semisenior"],
                              h=coeficientes["maximo_y_semisenior"],
                              funcion=fdp_tiempo_salida_semisenior)


def obtener_tiempo_resolucion_senior() -> int:
    return metodo_del_rechazo(a=0,
                              b=coeficientes["maximo_x_senior"],
                              h=coeficientes["maximo_y_senior"],
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
