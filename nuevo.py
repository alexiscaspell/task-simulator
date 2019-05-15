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

        tiempos_inicio_tareas = list(map(lambda tsk:tsk.tiempo_creacion,lista_tareas))

        desplazamiento = bisect.bisect_right(tiempos_inicio_tareas,nueva_tarea.tiempo_creacion)
        resto = len(lista_tareas) - desplazamiento

        lista_tareas[desplazamiento:resto] = [nueva_tarea]

    return lista_tareas

def realizar_simulacion()->List[Metrica]:
    lista_tareas = configuracion.tareas

    if not lista_tareas:
        lista_tareas = tareas_random(configuracion.tiempo_fin_simulacion)

    data = Simulacion(configuracion,lista_tareas)

    return simular(data)

def hay_una_llegada(lista_tareas:List[Tarea],tiempo:int)->bool:
    return lista_tareas[0].tiempo_creacion<=tiempo

def simular(simulacion:Simulacion)->List[Metrica]:

    lista_tareas = simulacion.tareas

    while(len(lista_tareas)>0):

        tareas_procesar = []

        if(hay_una_llegada(lista_tareas,tiempo_sistema)):
            while(hay_una_llegada(lista_tareas,tiempo_sistema)):
                tareas_procesar.append(lista_tareas.pop(0))
            
            tareas_sin_asignar = asignar(tareas_procesar)

            lista_tareas = tareas_sin_asignar + lista_tareas
        
        simulacion.finalizar_tareas()
            
        simulacion.incrementar_tiempo_sistema()
    
    return simulacion.metricas()
    