from tareas import Tarea, TipoTarea,PefilProgramador
from enum import Enum
from numpy.random import choice
import configuracion

class Administrador:
    def __init__(self, nro_programadores):
        self.programadores = nro_programadores
        self.programadores_ocupados = 0
        self.tareas_en_progreso = []
        self.perfil = self.perfil if isinstance(self.perfil,PefilProgramador) else None
        self.tiempo_ocioso = 0
        self.ultimo_tiempo_ocioso = 0

    def programadores_disponibles(self):
        return self.programadores-self.programadores_ocupados

    def actualizar_tiempo_ocioso(self, tiempo):
        if tiempo<self.ultimo_tiempo_ocioso:
            return

        self.tiempo_ocioso += (tiempo-self.ultimo_tiempo_ocioso) * \
            self.programadores_disponibles()
        self.ultimo_tiempo_ocioso = tiempo

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        raise NotImplementedError(
            "Administrador no esta implementando 'alguien_puede_resolver'")

    def tiempo_resolucion_tarea(self, tarea):
        return configuracion.tiempo_de_resolucion(self.perfil.value, tarea.tipo_tarea.value)

    def resolver_tarea(self, tiempo_actual, tarea)->Tarea:
        self.programadores_ocupados += 1
        tarea.perfil=self.perfil
        tarea.tiempo_fin = tiempo_actual + \
            self.tiempo_resolucion_tarea(tarea)
        return tarea

    def finalizar_tarea(self, tarea: Tarea):
        self.programadores_ocupados -= 1


class AdministradorJuniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Junior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return self.programadores_disponibles() > 0 and tarea.tipo_tarea in [TipoTarea.Facil, TipoTarea.Normal]


class AdministradorSemiseniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Semisenior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return self.programadores_disponibles() > 0 and tarea.tipo_tarea != TipoTarea.Imposible


class AdministradorSeniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Senior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return self.programadores_disponibles() > 0


def crear_administrador(perfil: PefilProgramador, cantidad_programadores):
    if perfil == PefilProgramador.Junior:
        return AdministradorJuniors(cantidad_programadores)
    elif perfil == PefilProgramador.Semisenior:
        return AdministradorSemiseniors(cantidad_programadores)
    elif perfil == PefilProgramador.Senior:
        return AdministradorSeniors(cantidad_programadores)
