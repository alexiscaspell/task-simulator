import datetime
import json
import time

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import pylab
import scipy
import scipy.stats
from fitter import Fitter
from numpy.polynomial.polynomial import Polynomial
from scipy.optimize import curve_fit



#################################################################
# PARAMETROS
#################################################################

FECHA_INICIAL_INICIAL = datetime.datetime(2018, 1, 1)
FECHA_FINAL_TAREAS = datetime.datetime(2019,4,30)

RUTA_DATOS = "datos/tareas.json"
RUTA_CONFIG_SALIDA = "./config/fdp_config.json"

try:
     archivo = open(RUTA_DATOS)
except Exception:
    archivo = open("../"+RUTA_DATOS)
    pass
datos = json.load(archivo)


#################################################################
# CONVERSORES
#################################################################
def string_a_fecha(fecha_en_string):
    return dateutil.parser.parse(fecha_en_string)


def fecha_string_a_tiempo_simulacion(fecha_en_string):
    fecha = string_a_fecha(fecha_en_string)

    milisegundos = fecha.timestamp() - FECHA_INICIAL_INICIAL.timestamp()
    return int(milisegundos / (1000 * 60))


def resta_fecha_strings_a_tiempo_simulacion(fecha_1, fecha_2):
    resta = string_a_fecha(fecha_1) - string_a_fecha(fecha_2) 
    return int(resta.total_seconds() / 60)
    

#################################################################
# FUNCIONES
#################################################################
FACIL = "facil"
NORMAL = "normal"
DIFICIL = "dificil"
IMPOSIBLE = "imposible"

JUNIOR = "junior"
SEMISENIOR = "semisenior"
SENIOR = "senior"


# tiempos de llegadas
def obtener_tiempos_llegada():
    return [fecha_string_a_tiempo_simulacion(tarea['fecha_creacion']) for tarea in datos]


# TA por tipos
def obtener_tiempos_resolucion(tipo_perfil):
    return [
        resta_fecha_strings_a_tiempo_simulacion(tarea['fecha_fin'], tarea['fecha_inicio'])
        for tarea in datos
        if tarea['perfil'] == tipo_perfil
    ]


#################################################################
# TIPOS DE EJECUCION
#################################################################

def ver_intervalos_tiempos_llegadas():
    y = obtener_tiempos_llegada()
    y.sort()
    print(y)

    x = np.linspace(1, len(y), num=len(y))

    plt.plot(x, y, 'o')
    plt.legend(['puntos'], loc='best')
    plt.show()


def ver_tiempos_salidas(tipo_perfil):
    print(f"PERFIL: {tipo_perfil}\n")

    y = obtener_tiempos_resolucion(tipo_perfil)
    y.sort()

    print(y)

    x = np.linspace(0, len(y), num=len(y))

    plt.plot(x, y, 'o')
    plt.legend([tipo_perfil], loc='best')
    plt.show()


def generar_funcion_aproximada_llegadas(graficar = False):

    print(f"LLEGADAS\n")

    def funcion_aproximante(x, a, b):
        return a*x + b

    y = obtener_tiempos_llegada()
    y.sort()
    x = np.linspace(0, 1, num=len(y))

    param, param_cov = curve_fit(funcion_aproximante, x, y)
    coeficientes_resultado = [e for e in param]
    print(f'COEFICIENTES DE LA FUNCION: \n{coeficientes_resultado}\n')

    if graficar:
        ans = param[0]*x + param[1]

        plt.plot(x, y, 'o', color='red', label="data")
        plt.plot(x, ans, '--', color='blue', label="optimized data")
        plt.legend()
        plt.show()

    return coeficientes_resultado
    


def generar_funcion_aproximada_salidas(tipo_perfil, graficar = False):

    print(f"SALIDAS DE PERFIL: {tipo_perfil}\n")

    def funcion_aproximante(x, a, b):
        return a**x - b

    y = obtener_tiempos_resolucion(tipo_perfil)
    y.sort()
    x = np.linspace(0, 1, num=len(y))

    param, param_cov = curve_fit(funcion_aproximante, x, y)
    coeficientes_resultado = [e for e in param]
    print(f'COEFICIENTES DE LA FUNCION: \n{coeficientes_resultado}\n')

    if graficar:
        ans = param[0]**x - param[1]

        plt.plot(x, y, 'o', color='red', label="data")
        plt.plot(x, ans, '--', color='blue', label="optimized data")
        plt.legend()
        plt.show()

    return coeficientes_resultado


###########################################################################################
# EJECUCION
###########################################################################################

if __name__ == "__main__":

    # DATOS
    # ver_intervalos_tiempos_llegadas()

    # ver_tiempos_salidas(JUNIOR)
    # ver_tiempos_salidas(SEMISENIOR)
    # ver_tiempos_salidas(SENIOR)


    # APROXIMACIONES
    coeficientes = {}
    coeficientes["llegadas"] = generar_funcion_aproximada_llegadas()

    coeficientes["salidas_junior"] = generar_funcion_aproximada_salidas(JUNIOR)
    coeficientes["salidas_semisenior"] = generar_funcion_aproximada_salidas(SEMISENIOR)
    coeficientes["salidas_senior"] = generar_funcion_aproximada_salidas(SENIOR)

    # GUARDADO
    archivo_salida = open(RUTA_CONFIG_SALIDA,"w+")
    archivo_salida.write(json.dumps(coeficientes))