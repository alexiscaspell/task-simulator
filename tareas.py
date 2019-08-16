from typing import List
import configuracion
from configuracion import Configuracion
from enum import Enum
import json
import bisect

# ----------------------------------------------------
# CLASES
# ----------------------------------------------------


class TipoTarea(Enum):
    Caotica = "Caotico"
    Complicada = "Complicado"
    Simple = "Simple"
    Compleja = "Complejo"


class Tarea:
    def __init__(self, tarea_spec: dict):
        self.tipo_tarea = tarea_spec['tipo_tarea']
        self.perfil = tarea_spec['perfil']
        self.tiempo_creacion = tarea_spec['tiempo_creacion']
        self.tiempo_inicio = tarea_spec['tiempo_inicio']
        self.tiempo_fin = tarea_spec['tiempo_fin']

    def get_dict(self):
        return {'tipo_tarea': None if self.tipo_tarea is None else self.tipo_tarea.value,
                'perfil': None if self.perfil is None else self.perfil.value,
                'tiempo_creacion': self.tiempo_creacion,
                'tiempo_inicio': self.tiempo_inicio,
                'tiempo_fin': self.tiempo_fin,
                'fecha_creacion': self.fecha_creacion(),
                'fecha_inicio': self.fecha_inicio(),
                'fecha_fin': self.fecha_fin()
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
    raise NotImplementedError()


def intervalo_arribo_tarea_random(tipo_tarea: TipoTarea) -> int:
    return 0


def tarea_random(tiempo_sistema: int) -> Tarea:
    una_tarea={}
    una_tarea["tipo_tarea"] = tipo_tarea_random()
    una_tarea["tiempo_creacion"] = tiempo_sistema + \
        intervalo_arribo_tarea_random(una_tarea["tipo_tarea"])

    return Tarea(una_tarea)


def tareas_random(tiempo_fin_simulacion: int) -> List[Tarea]:
    '''Retorna una lista de tareas random en base al tiempo de fin y los datos de simulacion de la configuracion'''
    lista_tareas = []
    for t in range(0, configuracion.configuracion().tiempo_fin_simulacion):
        nueva_tarea = tarea_random(t)

        tiempos_inicio_tareas = list(
            map(lambda tsk: tsk.tiempo_creacion, lista_tareas))

        desplazamiento = bisect.bisect_right(
            tiempos_inicio_tareas, nueva_tarea.tiempo_creacion)
        resto = len(lista_tareas) - desplazamiento

        lista_tareas[desplazamiento:resto] = [nueva_tarea]

    return lista_tareas
