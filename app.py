from typing import List
from simulacion import Simulacion,Metrica
from tareas import Tarea,tareas_random
import bisect
from configuracion import configuracion,Configuracion

def cargar_tareas(path:str)->List[Tarea]:
    if not path:
        return None
    raise NotImplementedError()

def realizar_simulacion(tareas_file_path:str=None)->List[Metrica]:
    lista_tareas = cargar_tareas(tareas_file_path)

    if not lista_tareas:
        lista_tareas = tareas_random(configuracion().tiempo_fin_simulacion)

    data = Simulacion(configuracion, lista_tareas)

    return simular(data)

def hay_una_llegada(lista_tareas:List[Tarea],tiempo:int)->bool:
    return lista_tareas[0].tiempo_creacion<=tiempo

def asignar(lista_tareas:List[Tarea])->List[Tarea]:
    raise NotImplementedError()

def simular(simulacion:Simulacion)->List[Metrica]:

    lista_tareas = simulacion.tareas

    while(len(lista_tareas)>0):

        tareas_procesar = []

        if(hay_una_llegada(lista_tareas,simulacion.tiempo_sistema)):
            while(hay_una_llegada(lista_tareas,simulacion.tiempo_sistema)):
                tareas_procesar.append(lista_tareas.pop(0))
            
            tareas_sin_asignar = asignar(tareas_procesar)

            lista_tareas = tareas_sin_asignar + lista_tareas
        
        simulacion.finalizar_tareas()
            
        simulacion.incrementar_tiempo_sistema()
    
    return simulacion.metricas()
