from typing import List
from simulacion import Simulacion,Metrica,crear_eventos_llegada,Evento
from tareas import Tarea,tareas_random
import bisect
import configuracion
from configuracion import Configuracion,print
import json
from administradores import Administrador,crear_administrador,PefilProgramador

def cargar_tareas(path:str)->List[Tarea]:
    if not path:
        return None
    with open(path) as file:
        tareas_specs =json.load(file)
        return [Tarea(t) for t in tareas_specs]

def realizar_simulacion(tareas_file_path:str=None)->List[Metrica]:
    lista_tareas = cargar_tareas(tareas_file_path)

    if not lista_tareas:
        lista_tareas = tareas_random(configuracion.configuracion().tiempo_fin_simulacion)

    administradores = [crear_administrador(PefilProgramador.Junior,configuracion.configuracion().cantidad_juniors),crear_administrador(PefilProgramador.Semisenior,configuracion.configuracion().cantidad_semiseniors),crear_administrador(PefilProgramador.Senior,configuracion.configuracion().cantidad_seniors)]

    data = Simulacion(configuracion.configuracion(), lista_tareas,administradores)

    return simular(data)

def insertar_eventos(eventos:List[Evento],mas_eventos:List[Evento]):
    for e in mas_eventos:
        tiempos_eventos = list(map(lambda ev: ev.tiempo, eventos))

        desplazamiento = bisect.bisect_right(
            tiempos_eventos, e.tiempo)
        resto = len(eventos) - desplazamiento

        eventos[desplazamiento:resto] = [e]
    return eventos
        

def simular(simulacion:Simulacion)->List[Metrica]:

    print("Comenzando simulacion ...")

    eventos = crear_eventos_llegada(simulacion.tareas)

    procesados=0
    total=len(eventos)

    while(len(eventos)>0):

        procesados +=1

        evento = eventos.pop()

        simulacion.tiempo_sistema = evento.tiempo

        nuevos_eventos = simulacion.resolver(evento)

        procesados-=len(nuevos_eventos)

        eventos = insertar_eventos(eventos,nuevos_eventos)

        print(f"PROCESADOS {procesados} DE {total} EVENTOS")

    
    return simulacion.resultado_metricas()

if __name__ == "__main__":
    resultados = realizar_simulacion(configuracion.configuracion().archivo_datos)
    print(f"RESULTADOS: {resultados}")
