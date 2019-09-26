from typing import List,Tuple
from simulacion import Simulacion,Metrica,crear_eventos_llegada,Evento,crear_eventos_salida
from tareas import Tarea,tareas_random,string_a_fecha
import bisect
import configuracion
from configuracion import Configuracion,print
import json
from math import ceil
from administradores import Administrador,crear_administrador,PefilProgramador
import matplotlib.pyplot as plt


def cargar_tareas(path:str)->List[Tarea]:
    if not path:
        return None
    with open(path) as file:
        tareas_specs =json.load(file)
        f = lambda t: string_a_fecha(t["fecha_creacion"])
        tareas_specs.sort(key=f)

    return [Tarea(t) for t in tareas_specs]

def realizar_simulacion(tareas_file_path:str=None)->Tuple[Simulacion,List]:
    lista_tareas = cargar_tareas(tareas_file_path)

    if not lista_tareas:
        lista_tareas = tareas_random(configuracion.configuracion().tiempo_fin_simulacion)

    administradores = [crear_administrador(PefilProgramador.Junior,configuracion.configuracion().cantidad_juniors),crear_administrador(PefilProgramador.Semisenior,configuracion.configuracion().cantidad_semiseniors),crear_administrador(PefilProgramador.Senior,configuracion.configuracion().cantidad_seniors)]

    data = Simulacion(configuracion.configuracion(), lista_tareas,administradores)

    return simular(data)


def insertar_eventos(eventos:List[Evento],mas_eventos:List[Evento]):

    for e in mas_eventos:
        tiempos_eventos = list(map(lambda ev: ev.tiempo, eventos))

        desplazamiento = bisect.bisect_right(tiempos_eventos, e.tiempo)

        eventos.insert(desplazamiento,e)

    return eventos
        

def simular(simulacion:Simulacion)->Tuple[Simulacion,List]:

    print("Comenzando simulacion ...")

    #SOLO SE SIMULA LO QUE ESTA DENTRO DEL RANGO DE TIEMPO
    simulacion.tareas = list(filter(lambda t:t.tiempo_creacion<simulacion.tiempo_fin,simulacion.tareas))

    eventos = crear_eventos_llegada(simulacion.tareas)

    procesados=0
    total=len(eventos)

    while(simulacion.tiempo_sistema<simulacion.tiempo_fin):

        procesados +=1

        evento = eventos.pop(0) if len(eventos)>0 else None

        if evento is None:
            break

        simulacion.tiempo_sistema = evento.tiempo

        nuevos_eventos = simulacion.resolver(evento)

        eventos = insertar_eventos(eventos,nuevos_eventos)

        if procesados%ceil(0.1*total)==0:
            print(f"PROCESADOS {procesados} EVENTOS")

    print(f"TIEMPO FINAL: {simulacion.tiempo_sistema}")
    print(f"PROCESADOS {procesados} EVENTOS")

    # with open("realizadas.json","w+") as f:
    #     json.dump([t.get_dict() for t in simulacion.tareas_finalizadas],f)
    # with open("sin_terminar.json","w+") as f:
    #     json.dump([t.get_dict() for t in simulacion.tareas_asignadas],f)
    # with open("tareas.json","w+") as f:
    #     json.dump([t.get_dict() for t in simulacion.tareas],f)


    return simulacion,simulacion.resultado_metricas()

if __name__ == "__main__":
    simulacion,resultados = realizar_simulacion(configuracion.configuracion().archivo_datos)

    print(f"RESULTADOS: {resultados}")

    for m in simulacion.metricas:
        m.generar_grafico()
