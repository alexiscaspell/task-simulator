from tareas import Tarea, TipoTarea,PefilProgramador
from enum import Enum
from numpy.random import choice
import configuracion

class Administrador:
    def __init__(self, nro_programadores):
        self.programadores = nro_programadores
        self.perfil = self.perfil if isinstance(self.perfil,PefilProgramador) else None
        self.tiempo_ocioso = 0
        self.ultimo_tiempo_ocioso = 0
        self.tiempos_comprometidos = [0 for i in range(self.programadores)]

    def programadores_disponibles(self,tiempo):
        return len(list(filter(lambda tc: tc<tiempo,self.tiempos_comprometidos)))

    @property
    def menor_tiempo_comprometido(self):
        return min(self.tiempos_comprometidos)

    def actualizar_tiempo_ocioso(self, tiempo):
        if tiempo<self.ultimo_tiempo_ocioso:
            return

        self.tiempo_ocioso += (tiempo-self.ultimo_tiempo_ocioso) * \
            self.programadores_disponibles(tiempo)
        self.ultimo_tiempo_ocioso = tiempo

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        raise NotImplementedError(
            "Administrador no esta implementando 'alguien_puede_resolver'")

    def tiempo_resolucion_tarea(self, tarea):
        return configuracion.tiempo_de_resolucion(self.perfil.value, tarea.tipo_tarea.value)

    def resolver_tarea(self, tiempo_actual, tarea)->Tarea:
        tarea.perfil=self.perfil
        tiempo_resolucion = self.tiempo_resolucion_tarea(tarea) if tarea.tiempo_fin is None else tarea.tiempo_fin-tarea.tiempo_inicio
        tarea.tiempo_fin = tiempo_actual + tiempo_resolucion

        self.tiempos_comprometidos.sort()

        self.tiempos_comprometidos.pop(0)

        self.tiempos_comprometidos = [tarea.tiempo_fin] + self.tiempos_comprometidos

        return tarea

class AdministradorJuniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Junior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return tarea.tipo_tarea in [TipoTarea.Facil, TipoTarea.Normal]


class AdministradorSemiseniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Semisenior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return tarea.tipo_tarea != TipoTarea.Imposible


class AdministradorSeniors(Administrador):
    def __init__(self, nro_programadores):
        self.perfil = PefilProgramador.Senior
        Administrador.__init__(self, nro_programadores)

    def alguien_puede_resolver(self, tarea: Tarea) -> bool:
        return True


def crear_administrador(perfil: PefilProgramador, cantidad_programadores):
    if perfil == PefilProgramador.Junior:
        return AdministradorJuniors(cantidad_programadores)
    elif perfil == PefilProgramador.Semisenior:
        return AdministradorSemiseniors(cantidad_programadores)
    elif perfil == PefilProgramador.Senior:
        return AdministradorSeniors(cantidad_programadores)
