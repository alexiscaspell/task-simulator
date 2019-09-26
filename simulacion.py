import configuracion
import tareas
from tareas import TipoTarea
from abc import ABCMeta
from typing import List, Tuple
from administradores import Administrador
from tareas import Tarea
from configuracion import UnidadTiempo,print
import matplotlib.pyplot as plt
import numpy as np


class Metrica(ABCMeta):
    def __init__(self, metrica_spec):
        self.nombre = metrica_spec["nombre"]

        grafico = metrica_spec.get("grafico", {})
        self.formato_grafico = grafico.get("extension", "svg")
        self.guardar_grafico = grafico.get("activo", False)
        self.path_grafico = grafico.get("nombre_archivo", self.nombre)

    def calcular(self, simulacion):
        raise NotImplementedError(
            "Metodo a implementar por metrica no cumplido")

    def guardar_grafico(self):
        if self.guardar_grafico:
            plt.savefig(f"{self.path_grafico}.{self.formato_grafico}",
                        format=self.formato_grafico)
        plt.close()


class FactoryMetricas:

    @staticmethod
    def crear(metric_spec: dict) -> Metrica:
        if metric_spec["nombre"] == "tiempo_ocioso":
            return TiempoOcioso(metric_spec)
        elif metric_spec["nombre"] == "tiempo_resolucion_promedio":
            return TiempoDeResolucionPromedio(metric_spec)
        elif metric_spec["nombre"] == "porcentaje_tareas_realizadas":
            return PorcentajeDeTareasRealizadas(metric_spec)

###########################################################--- SIMULACION ---###########################################################


class Evento:
    def __init__(self, tarea):
        self.tarea = tarea

    @property
    def tiempo(self):
        raise NotImplementedError("Propiedad tiempo no encontrada")


class EventoLlegada(Evento):
    def __init__(self, tarea):
        if not tarea:
            raise ValueError("No se paso una tarea para el evento de llegada")
        self.tarea = tarea

    @property
    def tiempo(self):
        return self.tarea.tiempo_creacion


class EventoSalida(Evento):
    def __init__(self, tarea):
        if not tarea:
            raise ValueError("No se paso una tarea para el evento de salida")
        self.tarea = tarea

    @property
    def tiempo(self):
        return self.tarea.tiempo_fin


def crear_eventos_llegada(tareas: List[Tarea]) -> List[EventoLlegada]:
    return list(map(lambda t: EventoLlegada(t), tareas))


def crear_eventos_salida(tareas: List[Tarea]) -> List[EventoSalida]:
    return list(map(lambda t: EventoSalida(t), tareas))


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

    def _asignar(self, lista_tareas: List[Tarea]) -> Tuple[List, List]:
        '''Asigna las tareas que pueden ser asignadas y retorna tupla tareas_asignadas,tareas_sin_asignar'''
        tareas_sin_asignar = []
        tareas_asignadas = []

        while len(lista_tareas) > 0:
            tarea = lista_tareas.pop(0)

            posibles_resolutores = []

            for admin in self.administradores:
                if admin.alguien_puede_resolver(tarea):
                    posibles_resolutores.append(admin)

            def ordenamiento(a): return a.menor_tiempo_comprometido
            posibles_resolutores.sort(key=ordenamiento)

            admin = posibles_resolutores[0] if tarea.perfil is None else next(
                a for a in self.administradores if a.perfil == tarea.perfil)

            tarea_actualizada = admin.resolver_tarea(
                self.tiempo_sistema, tarea)

            tareas_asignadas.append(tarea_actualizada)

        return tareas_asignadas, tareas_sin_asignar

    def resolver(self, evento: Evento):
        '''Resuelve dependiendo del tipo de evento y retorna los nuevos eventos condicionales y no condicionales'''
        llegadas = []
        salidas = []

        for a in self.administradores:
            a.actualizar_tiempo_ocioso(self.tiempo_sistema)

        if(isinstance(evento, EventoLlegada)):
            print(f"LLEGADA DE {evento.tarea.tipo_tarea.value} ...")
            asignadas, sin_asignar = self._asignar([evento.tarea])
            llegadas = crear_eventos_llegada(sin_asignar)
            salidas = crear_eventos_salida(asignadas)

            # ACA SE GUARDAN LAS TAREAS QUE SE COMENZARON Y NUNCA SE TERMINARON
            self.tareas_asignadas = self.tareas_asignadas + \
                list(filter(lambda t: t.tiempo_fin >= self.tiempo_fin, asignadas))

        elif isinstance(evento, EventoSalida):
            print(f"SALIDA DE {evento.tarea.perfil.value} ...")
            self.tareas_finalizadas.append(evento.tarea)

        return llegadas+salidas

    def resultado_metricas(self):
        return list(map(lambda m: {m.nombre: m.calcular(self)}, self.metricas))

###########################################################--- METRICAS ---###########################################################


class TiempoOcioso:

    def __init__(self, data):
        Metrica.__init__(self, data)

    def calcular(self, simulacion: Simulacion):
        resultado = {}
        for a in simulacion.administradores:
            perfil = a.perfil
            porcentaje_ocioso = a.tiempo_ocioso / \
                (simulacion.tiempo_fin*a.programadores)
            resultado.update({perfil.value: porcentaje_ocioso})

        self.resultado = resultado

        return self.resultado

    def generar_grafico(self):

        tuplas = list(self.resultado.items())

        # tuplas.sort(key=lambda e: e[1])

        porcentajes = [float(f"{r[1]*100:3.2f}") for r in tuplas]
        perfiles = [t[0] for t in tuplas]

        x_pos = [i for i, _ in enumerate(perfiles)]

        plt.bar(x_pos, porcentajes, color='green',edgecolor ='black')
        plt.xlabel("Perfil")
        plt.ylabel(f"Porcentaje (%)")
        plt.title("PORCENTAJE DE TIEMPO OCIOSO")

        plt.xticks(x_pos, perfiles)

        plt.tight_layout()

        Metrica.guardar_grafico(self)


class TiempoDeResolucionPromedio:

    def __init__(self, data):
        self.unidad_tiempo = UnidadTiempo(
            data.get("unidad_tiempo", UnidadTiempo.Segundos))
        Metrica.__init__(self, data)

    def calcular(self, simulacion: Simulacion):
        tiempos_promedio_por_tipo_tarea = {}

        for tipo_tarea in TipoTarea:
            tareas_de_tipo_tarea: List[Tarea] = list(
                filter(lambda t: t.tipo_tarea == tipo_tarea, simulacion.tareas_finalizadas))
            cant_tareas = max(len(tareas_de_tipo_tarea), 1)

            promedio = sum(map(lambda t: t.tiempo_fin -
                               t.tiempo_creacion, tareas_de_tipo_tarea))/cant_tareas
            promedio = UnidadTiempo.Segundos.llevar_a(
                self.unidad_tiempo, promedio)
            tiempos_promedio_por_tipo_tarea.update(
                {tipo_tarea.value: promedio})

        self.resultado = tiempos_promedio_por_tipo_tarea

        return self.resultado

    def generar_grafico(self):

        tuplas = list(self.resultado.items())

        # tuplas.sort(key=lambda e: e[1])

        tiempos_promedio = [float(f"{r[1]:9.2f}") for r in tuplas]
        tipos_tarea = [t[0] for t in tuplas]

        x_pos = [i for i, _ in enumerate(tipos_tarea)]

        plt.bar(x_pos, tiempos_promedio, color='green',edgecolor ='black')
        plt.xlabel("Tarea")
        plt.ylabel(f"Tiempo ({self.unidad_tiempo.value})")
        plt.title("PROMEDIO DE RESOLUCION DE TAREAS")

        plt.xticks(x_pos, tipos_tarea)

        plt.tight_layout()

        Metrica.guardar_grafico(self)


class PorcentajeDeTareasRealizadas:

    def __init__(self, data):
        Metrica.__init__(self, data)

    def calcular(self, simulacion: Simulacion):
        self.resultado = len(simulacion.tareas_finalizadas) / \
            len(simulacion.tareas)

        return self.resultado

    def generar_grafico(self):

        _, ax = plt.subplots(subplot_kw=dict(aspect="equal"))

        etiquetas = ['Hechas', 'Restantes']
        porcentajes = [self.resultado, 1-self.resultado]

        def func(pct, allvals):
            return f"{pct:3.2f}%"

        explode = (0.1, 0) 
        wedges, _, _ = ax.pie(porcentajes,explode=explode ,autopct=lambda pct: func(pct, porcentajes),
                                          textprops=dict(color="w"),shadow=True,startangle=45,wedgeprops={"edgecolor": "0", 'linewidth': 1})
        # wedges, _, _ = ax.pie(porcentajes,explode=explode ,autopct=lambda pct: func(pct, porcentajes),
        #                                   textprops=dict(color="w"),wedgeprops={"edgecolor": "0", 'linewidth': 1})

        ax.legend(wedges, etiquetas,
                  title="Tareas",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        plt.title("PORCENTAJE DE TAREAS REALIZADAS")

        plt.tight_layout()

        Metrica.guardar_grafico(self)


if __name__ == "__main__":
    pass
