from typing import List
from simulacion import Simulacion,Metrica,crear_eventos_llegada,Evento
from tareas import Tarea,tareas_random,string_a_fecha
import bisect
import configuracion
from configuracion import Configuracion,print
import json
from math import ceil
from administradores import Administrador,crear_administrador,PefilProgramador

def cargar_tareas(path:str)->List[Tarea]:
    if not path:
        return None
    with open(path) as file:
        tareas_specs =json.load(file)
        f = lambda t: string_a_fecha(t["fecha_creacion"])
        tareas_specs.sort(key=f)

    return [Tarea(t) for t in tareas_specs]

def realizar_simulacion(tareas_file_path:str=None)->List[Metrica]:
    lista_tareas = cargar_tareas(tareas_file_path)

    if not lista_tareas:
        lista_tareas = tareas_random(configuracion.configuracion().tiempo_fin_simulacion)

    administradores = [crear_administrador(PefilProgramador.Junior,configuracion.configuracion().cantidad_juniors),crear_administrador(PefilProgramador.Semisenior,configuracion.configuracion().cantidad_semiseniors),crear_administrador(PefilProgramador.Senior,configuracion.configuracion().cantidad_seniors)]

    data = Simulacion(configuracion.configuracion(), lista_tareas,administradores)

    return simular(data)

def insertar_eventos(eventos:List[Evento],mas_eventos:List[Evento]):
    if len(eventos)>0:
        mas_eventos = [eventos.pop(0)]+mas_eventos

    return mas_eventos+eventos

# def insertar_eventos(eventos:List[Evento],mas_eventos:List[Evento]):

#     for e in mas_eventos:
#         tiempos_eventos = list(map(lambda ev: ev.tiempo, eventos))

#         desplazamiento = bisect.bisect_right(tiempos_eventos, e.tiempo)
#         # resto = len(eventos) - desplazamiento

#         # eventos = eventos[desplazamiento:]+[e]+eventos[:resto]
#         eventos.insert(desplazamiento,e)

#     return eventos
        

def simular(simulacion:Simulacion)->List[Metrica]:

    print("Comenzando simulacion ...")

    #SOLO SE SIMULA LO QUE ESTA DENTRO DEL RANGO DE TIEMPO
    simulacion.lista_tareas = list(filter(lambda t:t.tiempo_creacion<simulacion.tiempo_fin,simulacion.tareas))

    eventos = crear_eventos_llegada(simulacion.lista_tareas)

    procesados=0
    total=len(eventos)

    while(simulacion.tiempo_sistema<simulacion.tiempo_fin):
    # while(len(eventos)>0):

        procesados +=1

        evento = eventos.pop(0) if len(eventos)>0 else None

        if evento is None:
            continue

        simulacion.tiempo_sistema = evento.tiempo

        nuevos_eventos = simulacion.resolver(evento)


        #SE DESCARTAN LOS EVENTOS CON t>=tiempo_fin
        # nuevos_eventos_filtrados = list(filter(lambda e:e.tiempo<simulacion.tiempo_fin,nuevos_eventos))

        # eventos = insertar_eventos(eventos,nuevos_eventos_filtrados)
        eventos = insertar_eventos(eventos,nuevos_eventos)

        if procesados%ceil(0.1*total)==0:
            print(f"PROCESADOS {procesados} EVENTOS")

    print(f"TIEMPO FINAL: {simulacion.tiempo_sistema}")
    print(f"PROCESADOS {procesados} EVENTOS")

    
    return simulacion.resultado_metricas()

if __name__ == "__main__":
    resultados = realizar_simulacion(configuracion.configuracion().archivo_datos)
    print(f"RESULTADOS: {resultados}")
