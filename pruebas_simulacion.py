import json
import os
import app
import configuracion
from configuracion import Configuracion

if __name__ == "__main__":
    PATH_BASE = "./simulaciones"

    with open("./config/configuracion.json") as f:
        config = json.load(f)

    def armar_configuracion(juniors,ssrs,srs):
        config["cantidad_juniors"] = juniors
        config["cantidad_semiseniors"] = ssrs
        config["cantidad_seniors"] = srs

        
        for m in config["metricas"]:
            path_a_usar = f"{PATH_BASE}/{m['nombre']}"
            try:
                os.mkdir(f"{path_a_usar}")
            except Exception:
                pass
            m["grafico"]["nombre_archivo"] = f"{path_a_usar}/({juniors},{ssrs},{srs})"

        configuracion.config = Configuracion(config)

    def generar_combinaciones_equipos():
        return [(1,1,1),(3,1,1),(2,2,2),(1,2,3),(1,1,5),(7,1,1),(5,2,1),(1,5,1)]


    for e in generar_combinaciones_equipos():

        armar_configuracion(e[0],e[1],e[2])
        simulacion,_ = app.realizar_simulacion()

        for m in simulacion.metricas:
            m.generar_grafico()
