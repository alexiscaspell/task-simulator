import datetime
import time
import json

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import pylab
import scipy
import scipy.stats
from numpy.polynomial.polynomial import Polynomial
from scipy.optimize import curve_fit
from fitter import Fitter

FECHA_INICIAL_SIMULACION = datetime.datetime(2018, 1, 1)

#################################################################
# PARAMETROS
#################################################################

RUTA_DATOS = "../datos/tareas.json"

with open(RUTA_DATOS) as archivo:
    datos = json.load(archivo)


#################################################################
# CONVERSORES
#################################################################
def string_a_fecha(fecha_en_string):
    return dateutil.parser.parse(fecha_en_string)


def fecha_string_a_tiempo_simulacion(fecha_en_string):
    fecha = string_a_fecha(fecha_en_string)

    d1_ts = time.mktime(FECHA_INICIAL_SIMULACION.timetuple())
    d2_ts = time.mktime(fecha.timetuple())

    return int(int(d2_ts-d1_ts) / 60)


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


# IA
def obtener_intervalos_tiempos_llegada():
    tiempos = obtener_tiempos_llegada()
    tiempos.sort()

    tiempos_2 = [0] + tiempos[:-1]
    tiempos_2.sort()

    y = [x1 - x2 for (x1, x2) in zip(tiempos, tiempos_2)]
    y.sort()

    return y


# TA por tipos
def obtener_tiempos_resolucion(tipo_perfil):
    return [
        fecha_string_a_tiempo_simulacion(
            tarea['fecha_fin']) - fecha_string_a_tiempo_simulacion(tarea['fecha_inicio'])
        for tarea in datos
        if tarea['perfil'] == tipo_perfil
    ]


#################################################################
# TIPOS DE EJECUCION
#################################################################

def ver_intervalos_tiempos_llegadas():
    tiempos = obtener_tiempos_llegada()
    tiempos.sort()

    tiempos_2 = [0] + tiempos[:-1]
    tiempos_2.sort()

    y = [x1 - x2 for (x1, x2) in zip(tiempos, tiempos_2)]
    y.sort()

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


def ver_funciones_aproximadas_salidas(tipo_perfil):

    print(f"PERFIL: {tipo_perfil}\n")

    data = obtener_tiempos_resolucion(tipo_perfil)
    data.sort()

    y = []
    x = []
    coordenadas = []
    for tiempo in set(data):
        y = data.count(tiempo) / len(data)
        x = tiempo
        coordenadas.append((x, y))

    def f(e): return e[0]
    coordenadas.sort(key=f)

    x = list(map(f, coordenadas))
    y = list(map(lambda e: e[1], coordenadas))

    print(f"CANT. DATOS: {len(data)}")
    print(f"CANT. COORDENADAS: {len(coordenadas)}")
    print(f"\n")

    polinomio = scipy.interpolate.lagrange(
        x[0:len(coordenadas)], y[0:len(coordenadas)])
    print(f'POLINOMIO: \n{[e for e in Polynomial(polinomio).coef]}\n\n')
    print(f'MAXIMO POSIBLE: {coordenadas[-1]}\n\n')

    plt.plot(x, y, 'o', x, y, '-', x, polinomio(x), '--')
    plt.legend(['puntos', 'interpolacion', 'polinomio'], loc='best')
    plt.show()


def ver_funciones_aproximadas_llegada():

    def funcion_aproximante(x, a, b):
        return (a**x) - b

    y = obtener_intervalos_tiempos_llegada()
    y.sort()
    x = np.linspace(0, 1, num=len(y))

    param, param_cov = curve_fit(funcion_aproximante, x, y)
    print(f'COEFICIENTES DE LA FUNCION: {param}')

    ans = (param[0]**x) - param[1]

    plt.plot(x, y, 'o', color='red', label="data")
    plt.plot(x, ans, '--', color='blue', label="optimized data")
    plt.legend()
    plt.show()


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
    # ver_funciones_aproximadas_llegada()

    ver_funciones_aproximadas_salidas(JUNIOR)
    # ver_funciones_aproximadas_salidas(SEMISENIOR)
    # ver_funciones_aproximadas_salidas(SENIOR)
