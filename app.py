from typing import List
from simulacion import Simulacion,Metrica,crear_eventos_llegada,Evento
from tareas import Tarea,tareas_random,string_a_fecha
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

    for e in mas_eventos:
        tiempos_eventos = list(map(lambda ev: ev.tiempo, eventos))

        desplazamiento = bisect.bisect_right(tiempos_eventos, e.tiempo)
        resto = len(eventos) - desplazamiento

        eventos = eventos[desplazamiento:]+[e]+eventos[:resto]

    return eventos
        

def simular(simulacion:Simulacion)->List[Metrica]:

    print("Comenzando simulacion ...")

    eventos = crear_eventos_llegada(simulacion.tareas)

    procesados=0
    total=len(eventos)

    while(simulacion.tiempo_sistema<simulacion.tiempo_fin):

        procesados +=1

        evento = eventos.pop(0) if len(eventos)>0 else None

        if evento is None:
            continue

        simulacion.tiempo_sistema = evento.tiempo

        nuevos_eventos = simulacion.resolver(evento)

        total+=len(nuevos_eventos)-1

        eventos = insertar_eventos(eventos,nuevos_eventos)

        print(f"PROCESADOS {procesados}/{total} EVENTOS")

    print(f"TIEMPO FINAL: {simulacion.tiempo_sistema}")

    
    return simulacion.resultado_metricas()

if __name__ == "__main__":
    resultados = realizar_simulacion(configuracion.configuracion().archivo_datos)
    print(f"RESULTADOS: {resultados}")
