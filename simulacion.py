import configuracion
import tareas
from tareas import TipoTarea
from abc import ABCMeta
from typing import List,Tuple
from administradores import Administrador
from tareas import Tarea
from configuracion import UnidadTiempo
import matplotlib.pyplot as plt
import numpy as np


class Metrica(ABCMeta):
    def __init__(self,metrica_spec):
        self.nombre = metrica_spec["nombre"]

        grafico = metrica_spec.get("grafico",{})
        self.formato_grafico = grafico.get("extension","svg")
        self.guardar_grafico = grafico.get("activo",False)
        self.path_grafico = grafico.get("nombre_archivo",self.nombre)

    def calcular(self, simulacion):
        raise NotImplementedError(
            "Metodo a implementar por metrica no cumplido")
            
    def guardar_grafico(self):
        if self.guardar_grafico:
            plt.savefig(f"{self.path_grafico}.{self.formato_grafico}", format=self.formato_grafico)
        plt.close()

class FactoryMetricas:

    @staticmethod
    def crear(metric_spec: dict) -> Metrica:
        if metric_spec["nombre"]=="tiempo_ocioso":
            return TiempoOcioso(metric_spec)
        elif metric_spec["nombre"]=="tiempo_resolucion_promedio":
            return TiempoDeResolucionPromedio(metric_spec)
        elif metric_spec["nombre"]=="porcentaje_tareas_realizadas":
            return PorcentajeDeTareasRealizadas(metric_spec)
        
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
        return self.tarea.tiempo_fin

def crear_eventos_llegada(tareas:List[Tarea])->List[EventoLlegada]:
    return list(map(lambda t: EventoLlegada(t),tareas))
    
def crear_eventos_salida(tareas:List[Tarea])->List[EventoSalida]:
    return list(map(lambda t: EventoSalida(t),tareas))

class Simulacion:
    def __init__(self, configuracion, lista_tareas, administradores):
        self.configuracion = configuracion
        self.tareas = lista_tareas
        self.tareas_finalizadas = []
        self.tareas_asignadas = []
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

            posibles_resolutores = []

            for admin in self.administradores:
                if admin.alguien_puede_resolver(tarea):
                    posibles_resolutores.append(admin)

            ordenamiento = lambda a : a.menor_tiempo_comprometido
            posibles_resolutores.sort(key=ordenamiento)
            admin = posibles_resolutores[0]
            tarea_actualizada = admin.resolver_tarea(self.tiempo_sistema,tarea)
            tareas_asignadas.append(tarea_actualizada)
            
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

            #ACA SE GUARDAN LAS TAREAS QUE SE COMENZARON Y NUNCA SE TERMINARON
            self.tareas_asignadas = self.tareas_asignadas+list(filter(lambda t:t.tiempo_fin>=self.tiempo_fin,asignadas))

        elif isinstance(evento,EventoSalida):
            print(f"SALIDA DE {evento.tarea.perfil.value} ...")
            # admin = next(a for a in self.administradores if a.perfil==evento.tarea.perfil)
            # admin.finalizar_tarea(evento.tarea)
            self.tareas_finalizadas.append(evento.tarea)

        return llegadas+salidas

    def resultado_metricas(self):
        return list(map(lambda m: {m.nombre: m.calcular(self)}, self.metricas))

###########################################################--- METRICAS ---###########################################################
class TiempoOcioso:

    def __init__(self,data):
        Metrica.__init__(self,data)

    def calcular(self, simulacion: Simulacion):
        resultado = {}
        for a in simulacion.administradores:
            perfil = a.perfil
            porcentaje_ocioso = a.tiempo_ocioso/(simulacion.tiempo_fin*a.programadores)
            resultado.update({perfil.value:porcentaje_ocioso})

        self.resultado=resultado

        return self.resultado

    def generar_grafico(self):
        tiempos_ocio = [v*100 for v in self.resultado.values()]
        x = np.arange(len(self.resultado))
        plt.bar(x, tiempos_ocio)
        plt.xticks(x, tuple([k for k in self.resultado]))
        
        Metrica.guardar_grafico(self)

class TiempoDeResolucionPromedio:

    def __init__(self,data):
        self.unidad_tiempo=UnidadTiempo(data.get("unidad_tiempo",UnidadTiempo.Segundos))
        Metrica.__init__(self,data)

    def calcular(self, simulacion: Simulacion):
        tiempos_promedio_por_tipo_tarea = {}

        for tipo_tarea in TipoTarea:
            tareas_de_tipo_tarea:List[Tarea] = list(
                filter(lambda t: t.tipo_tarea == tipo_tarea, simulacion.tareas_finalizadas))
            cant_tareas = max(len(tareas_de_tipo_tarea), 1)
                
            promedio = sum(map(lambda t: t.tiempo_fin - t.tiempo_creacion, tareas_de_tipo_tarea))/cant_tareas
            promedio = UnidadTiempo.Segundos.llevar_a(self.unidad_tiempo,promedio)
            tiempos_promedio_por_tipo_tarea.update(
                {tipo_tarea.value: promedio})

        self.resultado = tiempos_promedio_por_tipo_tarea

        return self.resultado

    def generar_grafico(self):
        tiempos_promedio = self.resultado.values()
        x = np.arange(len(self.resultado))
        plt.bar(x, tiempos_promedio)
        plt.xticks(x, tuple([k for k in self.resultado]))
        Metrica.guardar_grafico(self)

class PorcentajeDeTareasRealizadas:
    
    def __init__(self,data):
        Metrica.__init__(self,data)

    def calcular(self, simulacion: Simulacion):
        self.resultado =  len(simulacion.tareas_finalizadas)/len(simulacion.tareas)

        return self.resultado

    def generar_grafico(self):
        labels = ['Hechas', 'Restantes']
        sizes = [self.resultado*100,(1-self.resultado)*100]
        colors = ['lightskyblue', 'gold']
        patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.axis('equal')
        plt.tight_layout()
        Metrica.guardar_grafico(self)

if __name__ == "__main__":
    pass
