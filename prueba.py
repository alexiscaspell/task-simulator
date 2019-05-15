import bisect

tiempos_inicio_tareas = [1,2,3,4,5,6,8,9]
nueva_tarea=7

desplazamiento = bisect.bisect_right(tiempos_inicio_tareas,nueva_tarea)
resto = len(tiempos_inicio_tareas) - desplazamiento

print(f'{desplazamiento}')
print(f'{resto}')

tiempos_inicio_tareas[desplazamiento:resto] = [nueva_tarea]

print(f'{tiempos_inicio_tareas}')