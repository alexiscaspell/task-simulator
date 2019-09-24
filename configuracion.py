from numpy.random import choice
import json
from datetime import datetime, timedelta
from enum import Enum
import builtins
from typing import List,Callable

config = None
FORMATO_SALIDA_FECHA = "%d/%m/%yT%H:%M:%SZ"


def print(algo, logging=None):
    if logging or configuracion and config.logging:
        return builtins.print(algo)


class UnidadTiempo(Enum):
    Segundos = "segundos"
    Minutos = "minutos"
    Horas = "horas"

    def llevar_a_minutos(self, un_tiempo: int) -> int:
        if self == UnidadTiempo.Segundos:
            return un_tiempo/60
        elif self == UnidadTiempo.Horas:
            return un_tiempo*60
        return un_tiempo

    def llevar_a_horas(self, un_tiempo: int) -> int:
        if self == UnidadTiempo.Segundos:
            return un_tiempo/(60*60)
        elif self == UnidadTiempo.Minutos:
            return un_tiempo/60
        return un_tiempo

    def llevar_a_segundos(self, un_tiempo: int) -> int:
        if self == UnidadTiempo.Minutos:
            return un_tiempo*60
        elif self == UnidadTiempo.Horas:
            return un_tiempo*60*60
        return un_tiempo


class ModuloExterno():
    def __init__(self, modulo_spec):
        self.nombre_funcion = modulo_spec["funcion"]
        self.nombre_modulo = self.path_a_modulo(modulo_spec["modulo"])

        self.modulo = __import__(self.nombre_modulo, fromlist=[''])
        self.funcion = getattr(self.modulo,self.nombre_funcion)

    def path_a_modulo(self,path):
        return str(path).replace("/",".").replace(".py","")

    def invocar(self, *args,**kwargs):
        return self.funcion(*args,**kwargs)


class Configuracion():
    def __init__(self, configuracion_spec):
        self.logging = configuracion_spec.get("logging", False)
        self.cantidad_juniors = configuracion_spec['cantidad_juniors']
        self.cantidad_semiseniors = configuracion_spec['cantidad_semiseniors']
        self.cantidad_seniors = configuracion_spec['cantidad_seniors']
        self.archivo_datos = configuracion_spec.get('archivo_datos',None)
        self.formato_fecha = configuracion_spec.get(
            "formato_fecha", "%d/%m/%y")
        self.fecha_inicial = datetime.strptime(configuracion_spec.get(
            'fecha_inicial', datetime.strftime(datetime.now(), self.formato_fecha)), self.formato_fecha)
        self.unidad_tiempo = UnidadTiempo(
            configuracion_spec.get('unidad_tiempo', "segundos"))
        self.tiempo_fin_simulacion = self.unidad_tiempo.llevar_a_segundos(
            configuracion_spec['tiempo_fin_simulacion'])
        self.intervalo_arribo_tarea:Callable = ModuloExterno(
            configuracion_spec["intervalo_arribo_tareas"]).funcion
        self.tiempo_de_resolucion:Callable = ModuloExterno(
            configuracion_spec["tiempo_de_resolucion"]).funcion
        self.dias_laborales_mes = configuracion_spec.get(
            "dias_laborales_mes", 20)
        self.horas_laborales_dia = configuracion_spec.get(
            "horas_laborales_dia", 8)
        self.probabilidades_tareas = configuracion_spec["probabilidades_tareas"]
        self.fecha_fin = self.calcular_fecha_fin()
        self.metricas_spec = configuracion_spec.get("metricas",[])

    def calcular_fecha_fin(self) -> datetime:
        return self.calcular_fecha(self.fecha_inicial, self.tiempo_fin_simulacion, UnidadTiempo.Segundos)

    def calcular_fecha(self, fecha_inicial: datetime, tiempo_fin: int, unidad_tiempo: UnidadTiempo = UnidadTiempo.Segundos) -> datetime:
        tiempo_fin_minutos = unidad_tiempo.llevar_a_minutos(tiempo_fin)
        HORAS_LABORALES = self.horas_laborales_dia
        DIAS_LABORALES = self.dias_laborales_mes
        dias = round(tiempo_fin_minutos/(HORAS_LABORALES*60))
        meses_laborales = round(dias/DIAS_LABORALES)
        dias_laborales = round(max(meses_laborales*30, dias))
        minutos = tiempo_fin_minutos-dias*HORAS_LABORALES*60
        # print(f"CALCULANDO FECHA CON: tm:{tiempo_fin_minutos},d:{dias},ml:{meses_laborales},dl:{dias_laborales},m:{minutos}",logging=self.logging)
        fecha_fin = fecha_inicial + \
            timedelta(days=dias_laborales)+timedelta(minutes=minutos)
        return fecha_fin

    def __str__(self):
        return str(self.dict())

    def dict(self):
        return {
            "cantidad_juniors": self.cantidad_juniors,
            "cantidad_semiseniors": self.cantidad_semiseniors,
            "cantidad_seniors": self.cantidad_seniors,
            "tiempo_fin_simulacion": self.tiempo_fin_simulacion,
            "formato_fecha": self.formato_fecha,
            "fecha_inicial": datetime.strftime(self.fecha_inicial, FORMATO_SALIDA_FECHA),
            "unidad_tiempo": UnidadTiempo.Horas.value,
            "fecha_fin": datetime.strftime(self.fecha_fin, FORMATO_SALIDA_FECHA)
        }


def tiempo_de_resolucion(perfil: str, tipo_tarea: str) -> int:
    '''Retorna el tiempo de resolucion de de una tarea en base al perfil y el tipo de tarea'''
    return config.tiempo_de_resolucion(perfil,tipo_tarea)

# ----------------------------------------------------
# CONFIGURACION DE ARCHIVO
# ----------------------------------------------------


def obtener_configuracion_de_archivo(path) -> Configuracion:
    with open(path, encoding='utf-8') as json_file:
        text = json_file.read()
        json_data = json.loads(text)
    return Configuracion(json_data)


config = obtener_configuracion_de_archivo("./configuracion.json")


def configuracion():
    return config
