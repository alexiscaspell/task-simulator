from typing import List
import configuracion
from configuracion import Configuracion
from enum import Enum
import json
import bisect
from numpy.random import choice
from typing import Dict
from configuracion import UnidadTiempo
from datetime import datetime
import time
from math import ceil

# ----------------------------------------------------
# CLASES
# ----------------------------------------------------

class PefilProgramador(Enum):
    Junior = "junior"
    Semisenior = "semisenior"
    Senior = "senior"

class TipoTarea(Enum):
    Facil = "facil"
    Normal = "normal"
    Dificil = "dificil"
    Imposible = "imposible"

def string_a_fecha(fecha_en_string):
    try:
        datetime.strptime(fecha_en_string,configuracion.configuracion().formato_fecha)
    except Exception:
        return datetime.strptime(fecha_en_string,"%Y-%m-%d %H:%M:%S.%f")

def fecha_string_a_tiempo_simulacion(fecha_en_string):
    fecha = string_a_fecha(fecha_en_string)

    return int((fecha-configuracion.configuracion().fecha_inicial).total_seconds())
    
    # d1_ts = time.mktime(configuracion.configuracion().fecha_inicial.timetuple())
    # d2_ts = time.mktime(fecha.timetuple())
    
    # return UnidadTiempo.Minutos.llevar_a_segundos(int(int(d2_ts-d1_ts) / 60))

class Tarea:
    def __init__(self, tarea_spec: dict):
        self.tipo_tarea = TipoTarea(tarea_spec['tipo'])
        perfil=tarea_spec.get('perfil',None)
        self.perfil = PefilProgramador(perfil) if perfil is  not None else None
        self.tiempo_creacion = tarea_spec['tiempo_creacion'] if "tiempo_creacion" in tarea_spec else fecha_string_a_tiempo_simulacion(tarea_spec["fecha_creacion"])

        tiempo_inicio = tarea_spec.get('tiempo_inicio',None)
        tiempo_inicio = tiempo_inicio if tiempo_inicio is not None and "fecha_inicio" in tarea_spec else fecha_string_a_tiempo_simulacion(tarea_spec["fecha_inicio"])
        self.tiempo_inicio =  tiempo_inicio

        tiempo_fin = tarea_spec.get('tiempo_fin',None)
        tiempo_fin = tiempo_fin if tiempo_fin is not None and "fecha_fin" in tarea_spec else fecha_string_a_tiempo_simulacion(tarea_spec["fecha_fin"])
        self.tiempo_fin =  tiempo_fin

    def get_dict(self):
        return {'tipo': None if self.tipo_tarea is None else self.tipo_tarea.value,
                'perfil': None if self.perfil is None else self.perfil.value,
                'tiempo_creacion': self.tiempo_creacion,
                'tiempo_inicio': self.tiempo_inicio,
                'tiempo_fin': self.tiempo_fin,
                'fecha_creacion': str(self.fecha_creacion()),
                'fecha_inicio': str(self.fecha_inicio()),
                'fecha_fin': str(self.fecha_fin())
                }

    def fecha_creacion(self):
        c = configuracion.configuracion()
        return c.calcular_fecha(c.fecha_inicial, self.tiempo_creacion)

    def fecha_inicio(self):
        c = configuracion.configuracion()
        return c.calcular_fecha(c.fecha_inicial, self.tiempo_inicio)

    def fecha_fin(self):
        c = configuracion.configuracion()
        return c.calcular_fecha(c.fecha_inicial, self.tiempo_fin)

    def id(self):
        return self.tipo_tarea, self.tiempo_creacion

    def __hash__(self):
        return hash(self.id())

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return json.dumps(self.get_dict())

    def __eq__(self, other):
        return self.id() == other.id()

# ----------------------------------------------------
# FUNCIONES
# ----------------------------------------------------


def tipo_tarea_random() -> TipoTarea:
    mapa_probabilidades:Dict=configuracion.configuracion().probabilidades_tareas
    tipos_tarea= [TipoTarea(t) for t in mapa_probabilidades]
    probabilidades= [mapa_probabilidades[t.value] for t in tipos_tarea]
    
    return choice(tipos_tarea, size=1,p=probabilidades,replace=True)[0]

def intervalo_arribo_tarea_random(tipo_tarea: TipoTarea) -> int:
    return configuracion.configuracion().intervalo_arribo_tarea(tipo_tarea)

def tarea_random(tiempo_sistema: int) -> Tarea:
    una_tarea={}
    una_tarea["tipo"] = tipo_tarea_random()
    una_tarea["tiempo_creacion"] = tiempo_sistema + \
        intervalo_arribo_tarea_random(una_tarea["tipo"])

    return Tarea(una_tarea)


def tareas_random(tiempo_fin_simulacion: int) -> List[Tarea]:
    '''Retorna una lista de tareas random en base al tiempo de fin y los datos de simulacion de la configuracion'''
    lista_tareas = []
    t = 0

    while (t<configuracion.configuracion().tiempo_fin_simulacion):
        nueva_tarea = tarea_random(t)

        tiempos_inicio_tareas = list(
            map(lambda tsk: tsk.tiempo_creacion, lista_tareas))

        desplazamiento = bisect.bisect_right(
            tiempos_inicio_tareas, nueva_tarea.tiempo_creacion)
        # resto = len(lista_tareas) - desplazamiento

        lista_tareas.insert(desplazamiento,nueva_tarea)

        t=nueva_tarea.tiempo_creacion

        if len(lista_tareas)%100==0:
            print(f"GENERADAS {len(lista_tareas)} TAREAS")

        # lista_tareas = lista_tareas[desplazamiento:] + [nueva_tarea] + lista_tareas[:resto]

    return lista_tareas
