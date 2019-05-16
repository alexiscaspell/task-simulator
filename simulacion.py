import configuracion
import tareas
from tareas import TipoTarea

class Simulacion:
    def __init__(self,configuracion,lista_tareas):
        self.configuracion = configuracion
        self.tareas = lista_tareas
        metricas_spec = configuracion.configuracion().metricas_spec()
        self.metricas = list(map(lambda m : FactoryMetricas.crear(m),metricas_spec))

     def finalizar_tareas(self):
         raise NotImplementedError("No implementado aun")

    def incrementar_tiempo_sistema(self):
        self.tiempo_sistema += 1
    
    def metricas(self):
        return list(map(lambda m: m.calcular(self),self.metricas))




class Metrica(A):
    def calcular(self,simulacion:Simulacion):
        raise NotImplementedError("Metodo a implementar por metrica no cumplido")

  class TiempoOcioso(Metrica):

  def calcular(self):
    return [{"perfil":e["perfil"].value,"porcentaje":e["tiempo_ocioso"]/(max(1,self.tiempo_finalizacion*e["cantidad_programadores"]))} for e in self.tiempos_de_ocio]

  def agregar_tiempo_ocioso(self,perfil,cantidad_personas_al_pedo):
    mapa_de_ocio = next(mapa for mapa in self.tiempos_de_ocio if mapa["perfil"]==perfil)
    mapa_de_ocio.update({"tiempo_ocioso":mapa_de_ocio["tiempo_ocioso"]+cantidad_personas_al_pedo})

class TiempoDeResolucionPromedio(Metrica):

  def calcular(self,simulacion:Simulacion):
    tiempos_promedio_por_tipo_tarea = []

    for tipo_tarea in TipoTarea:
      tareas_de_tipo_tarea = list(filter(lambda t: t.tipo_tarea==tipo_tarea,simulacion.tareas_realizadas))
      cant_tareas = max(len(tareas_de_tipo_tarea),1)
      promedio = sum(map(lambda t : t.fecha_fin-t.fecha_creacion ,tareas_de_tipo_tarea))/cant_tareas
      tiempos_promedio_por_tipo_tarea.append({tipo_tarea.value:promedio})
      
    return tiempos_promedio_por_tipo_tarea

class PorcentajeDeTareasRealizadas(Metrica):
  
  def calcular(self,simulacion:Simulacion):
    H = len(simulacion.tareas_realizadas)
    L = len(simulacion.tareas)
    total = max(1,H+L)

    return H/total