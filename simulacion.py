import configuracion
import tareas
from tareas import TipoTarea
from abc import ABCMeta
from typing import List,Tuple
from administradores import Administrador
from tareas import Tarea

class Metrica(ABCMeta):
    def calcular(self, simulacion):
        raise NotImplementedError(
            "Metodo a implementar por metrica no cumplido")

class FactoryMetricas:

    @staticmethod
    def crear(metric_spec: dict) -> Metrica:
        raise NotImplementedError()

###########################################################--- SIMULACION ---###########################################################
class Evento:
    def __init__(self,tarea):
        self.tarea = tarea
    @property    
    def tiempo(self):
        raise NotImplementedError("Propiedad tiempo no encontrada")

class EventoLlegada(Evento):
    def __init__(self,tarea):
        if not tarea:
            raise ValueError("No se paso una tarea para el evento de llegada")
        self.tarea = tarea

    @property    
    def tiempo(self):
        return self.tarea.tiempo_creacion

class EventoSalida(Evento):
    def __init__(self,tarea):
        if not tarea:
            raise ValueError("No se paso una tarea para el evento de salida")
        self.tarea = tarea

    @property    
    def tiempo(self):
        return self.tarea.tiempo_finalizacion

def crear_eventos_llegada(tareas:List[Tarea])->List[EventoLlegada]:
    return list(map(lambda t: EventoLlegada(t),tareas))
    
def crear_eventos_salida(tareas:List[Tarea])->List[EventoSalida]:
    return list(map(lambda t: EventoSalida(t),tareas))

class Simulacion:
    def __init__(self, configuracion, lista_tareas, administradores):
        self.configuracion = configuracion
        self.tareas = lista_tareas
        self.tareas_finalizadas = []
        metricas_spec = self.configuracion.metricas_spec
        self.metricas = list(
            map(lambda m: FactoryMetricas.crear(m), metricas_spec))
        self.tiempo_sistema = 0
        self.tiempo_fin = configuracion.tiempo_fin_simulacion
        self.administradores = administradores

    def _asignar(self, lista_tareas: List[Tarea]) -> Tuple[List,List]:
        '''Asigna las tareas que pueden ser asignadas y retorna tupla tareas_asignadas,tareas_sin_asignar'''
        tareas_sin_asignar = []
        tareas_asignadas = []

        while len(lista_tareas) > 0:
            tarea = lista_tareas.pop(0)

            se_puede_resolver = False

            for admin in self.administradores:
                if admin.alguien_puede_resolver(tarea):
                    tarea_actualizada = admin.resolver_tarea(self.tiempo_sistema,tarea)
                    tareas_asignadas.append(tarea_actualizada)
                    se_puede_resolver=True
                    break
            if not se_puede_resolver:    
                tareas_sin_asignar.append(tarea)


        return tareas_asignadas,tareas_sin_asignar

    def resolver(self,evento:Evento):
        '''Resuelve dependiendo del tipo de evento y retorna los nuevos eventos condicionales y no condicionales'''
        llegadas=[]
        salidas=[]

        for a in self.administradores:
            a.actualizar_tiempo_ocioso(self.tiempo_sistema)

        if(isinstance(evento,EventoLlegada)):
            print(f"LLEGADA DE {evento.tarea.tipo_tarea.value} ...")
            asignadas,sin_asignar = self._asignar([evento.tarea])
            llegadas = crear_eventos_llegada(sin_asignar)
            salidas = crear_eventos_salida(asignadas)
            self.tareas_finalizadas = self.tareas_finalizadas + asignadas

        elif isinstance(evento,EventoSalida):
            print(f"SALIDA DE {evento.tarea.perfil.value} ...")
            admin = next(a for a in self.administradores if a.perfil==evento.tarea.perfil)
            admin.finalizar_tarea(evento.tarea)

        return llegadas+salidas

    def resultado_metricas(self):
        return list(map(lambda m: m.calcular(self), self.metricas))

###########################################################--- METRICAS ---###########################################################
class TiempoOcioso(Metrica):

    def calcular(self):
        return [{"perfil": e["perfil"].value, "porcentaje":e["tiempo_ocioso"]/(max(1, self.tiempo_finalizacion*e["cantidad_programadores"]))} for e in self.tiempos_de_ocio]

    def agregar_tiempo_ocioso(self, perfil, cantidad_personas_al_pedo):
        mapa_de_ocio = next(
            mapa for mapa in self.tiempos_de_ocio if mapa["perfil"] == perfil)
        mapa_de_ocio.update(
            {"tiempo_ocioso": mapa_de_ocio["tiempo_ocioso"]+cantidad_personas_al_pedo})


class TiempoDeResolucionPromedio(Metrica):

    def calcular(self, simulacion: Simulacion):
        tiempos_promedio_por_tipo_tarea = []

        for tipo_tarea in TipoTarea:
            tareas_de_tipo_tarea = list(
                filter(lambda t: t.tipo_tarea == tipo_tarea, simulacion.tareas_realizadas))
            cant_tareas = max(len(tareas_de_tipo_tarea), 1)
            promedio = sum(map(lambda t: t.fecha_fin -
                               t.fecha_creacion, tareas_de_tipo_tarea))/cant_tareas
            tiempos_promedio_por_tipo_tarea.append(
                {tipo_tarea.value: promedio})

        return tiempos_promedio_por_tipo_tarea


class PorcentajeDeTareasRealizadas(Metrica):

    def calcular(self, simulacion: Simulacion):
        H = len(simulacion.tareas_realizadas)
        L = len(simulacion.tareas)
        total = max(1, H+L)

        return H/total


if __name__ == "__main__":
    pass
