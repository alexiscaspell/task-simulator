from numpy.random import choice
import json
from datetime import datetime, timedelta
from enum import Enum
import builtins
from typing import List,Callable
from importlib import import_module

config = None
FORMATO_SALIDA_FECHA = "%d/%m/%yT%H:%M:%SZ"

def cambiar_a_hora_laboral(fecha: datetime,horario_laboral_inicial,horario_laboral_salida) -> datetime:

    cumple_dia_laboral = fecha.strftime("%A") != "Saturday" and fecha.strftime("%A") != "Sunday"
    cumple_hora_laboral = horario_laboral_inicial <= fecha.hour <= horario_laboral_salida
    
    if not cumple_dia_laboral:
        dias_a_sumar = 1 if fecha.strftime("%A") == "Sunday" else 2
        return cambiar_a_hora_laboral(fecha + timedelta(days=dias_a_sumar),horario_laboral_inicial,horario_laboral_salida)        

    if not cumple_hora_laboral:
        
        if fecha.hour < horario_laboral_inicial:
            fecha = fecha.replace(hour=24 - horario_laboral_salida + horario_laboral_inicial + fecha.hour)
            fecha += timedelta(days=1)

        if horario_laboral_salida < fecha.hour:
            fecha = fecha.replace(hour=horario_laboral_inicial + fecha.hour - horario_laboral_salida)
            fecha += timedelta(days=1)
        
        return cambiar_a_hora_laboral(fecha,horario_laboral_inicial,horario_laboral_salida)

    return fecha


def print(algo, logging=None):
    if logging or configuracion and config.logging:
        return builtins.print(algo)

# HORAS_LABORALES = 9
# DIAS_LABORALES = 20
HORAS_LABORALES = 24
DIAS_LABORALES = 31

class UnidadTiempo(Enum):
    Segundos = "segundos"
    Minutos = "minutos"
    Horas = "horas"
    Dias = "dias"
    Meses = "meses"
    Años = "años"

    def orden_de_unidades(self):
        return {
            UnidadTiempo.Segundos:60,
            UnidadTiempo.Minutos:60,
            UnidadTiempo.Horas:HORAS_LABORALES,
            UnidadTiempo.Dias:DIAS_LABORALES,
            UnidadTiempo.Meses:12,
            UnidadTiempo.Años:1
        }


    def llevar_a(self,unidad,un_tiempo):
        if self==unidad:
            return un_tiempo

        unidades = list(self.orden_de_unidades().keys())
        valores = list(self.orden_de_unidades().values())

        indice_propio = unidades.index(self)
        indice_unidad = unidades.index(unidad)

        es_menor_unidad = indice_propio<indice_unidad

        if es_menor_unidad:
            lista = valores[indice_propio:indice_unidad]
        else:
            lista = valores[indice_unidad:indice_propio]

        k = 1
        for v in lista:
            k = k*v 

        return un_tiempo/k if es_menor_unidad else un_tiempo*k

    def llevar_a_minutos(self, un_tiempo: int) -> int:
        return self.llevar_a(UnidadTiempo.Minutos,un_tiempo)

    def llevar_a_horas(self, un_tiempo: int) -> int:
        return self.llevar_a(UnidadTiempo.Horas,un_tiempo)

    def llevar_a_segundos(self, un_tiempo: int) -> int:
        return self.llevar_a(UnidadTiempo.Segundos,un_tiempo)

class ModuloExterno():
    def __init__(self, modulo_spec):
        self.nombre_funcion = modulo_spec["funcion"]
        nombre_modulo_entero = self.path_a_modulo(modulo_spec["modulo"])
        self.nombre_modulo = nombre_modulo_entero.split(".").pop()
        self.carpeta = nombre_modulo_entero.replace(f".{self.nombre_modulo}","").replace(self.nombre_modulo,"")

        # self.modulo = __import__(self.nombre_modulo, fromlist=[self.carpeta])
        self.modulo = import_module(nombre_modulo_entero)
        self.funcion = getattr(self.modulo,self.nombre_funcion)

    def path_a_modulo(self,path):
        return str(path).replace("/",".").replace(".py","")

    def invocar(self, *args,**kwargs):
        return self.funcion(*args,**kwargs)

class FuncionDeProbabilidad:
    def __init__(self,fdp_spec):
        self.unidad_tiempo = UnidadTiempo(fdp_spec.get("unidad_tiempo",UnidadTiempo.Minutos))
        self.modulo = ModuloExterno(fdp_spec)

    @property   
    def funcion(self,*args,**kwargs):
        return lambda *args,**kwargs: self.unidad_tiempo.llevar_a_segundos(self.modulo.funcion(*args,**kwargs))


class Configuracion():
    def __init__(self, configuracion_spec):
        self.logging = configuracion_spec.get("logging", False)
        self.cantidad_juniors = configuracion_spec['cantidad_juniors']
        self.cantidad_semiseniors = configuracion_spec['cantidad_semiseniors']
        self.cantidad_seniors = configuracion_spec['cantidad_seniors']
        self.archivo_datos = configuracion_spec.get('archivo_datos',None)

        if not configuracion_spec.get("cargar_de_archivo",False):
            self.archivo_datos = None

        self.formato_fecha = configuracion_spec.get(
            "formato_fecha", "%d/%m/%y")
        self.fecha_inicial = datetime.strptime(configuracion_spec.get(
            'fecha_inicial', datetime.strftime(datetime.now(), self.formato_fecha)), self.formato_fecha)
        self.unidad_tiempo = UnidadTiempo(configuracion_spec.get('unidad_tiempo', "segundos"))
        self.tiempo_fin_simulacion = self.unidad_tiempo.llevar_a_segundos(configuracion_spec['tiempo_fin_simulacion'])
        self.intervalo_arribo_tarea:Callable = FuncionDeProbabilidad(
            configuracion_spec["intervalo_arribo_tareas"]).funcion
        self.tiempo_de_resolucion:Callable = FuncionDeProbabilidad(
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
        fecha_fin = fecha_inicial + timedelta(minutes=unidad_tiempo.llevar_a_minutos(tiempo_fin))

        return cambiar_a_hora_laboral(fecha_fin,fecha_inicial.hour,fecha_inicial.hour+self.horas_laborales_dia)

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


config = obtener_configuracion_de_archivo("./config/configuracion.json")


def configuracion():
    return config
