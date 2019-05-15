from typing import List
import bisect

def tipo_tarea_random()->TipoTarea:
    return un_tipo_tarea

def intervalo_arribo_tarea_random(tipo_tarea:TipoTarea)->int:
    return 0

def tarea_random(tiempo_sistema:int)->Tarea:
    una_tarea = Tarea()
    una_tarea.tipo_tarea = tipo_tarea_random()
    una_tarea.tiempo_creacion = tiempo_sistema + intervalo_arribo_tarea_random(una_tarea.tipo_tarea)

    return una_tarea

def tareas_random(tiempo_fin_simulacion:int)->List[Tarea]:
    '''Retorna una lista de tareas random en base al tiempo de fin y los datos de simulacion de la configuracion'''
    lista_tareas = []
    for t in range(0,configuracion.tiempo_fin_simulacion):
        nueva_tarea = tarea_random(t)
        i = bisect.bisect_right(list(map(lambda tsk:tsk.tiempo_creacion,lista_tareas)),nueva_tarea.tiempo_creacion)
        lista_tareas[(len(lista_tareas)-,0):i]

        



lista_tareas = tareas_random(configuracion.tiempo_fin_simulacion)