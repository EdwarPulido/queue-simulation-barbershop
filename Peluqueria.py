# -*- coding: utf-8 -*-

"""
Simulación de una peluquería usando eventos discretos con SimPy.
Simula la atención de clientes a través de cortes y servicios estéticos variados.
"""

import random
import simpy
import math
import numpy as np

# ============================================================
# CONFIGURACIÓN Y PARÁMETROS
# ============================================================

SEMILLA = 10
NUMERO_PELUQUEROS = 10
TIEMPO_LLEGADA_MEDIA = 15  # minutos
TOTAL_CLIENTES = np.random.poisson(15)

# Tiempos de servicio (en minutos)
SERVICIOS = {
    "corte_hombre": (15, 35),
    "corte_mujer": (35, 45),
    "corte_especial": (45, 55),
    "uñas_manos": (55, 60),
    "uñas_pies": (60, 70),
}

# Variables globales para métricas
tiempo_espera_total = 0.0
tiempo_servicio_total = 0.0
tiempo_final = 0.0


# ============================================================
# FUNCIONES DE SERVICIO
# ============================================================

def servicio(env, cliente, tipo, tiempo_min, tiempo_max):
    global tiempo_servicio_total
    duracion = tiempo_min + (tiempo_max - tiempo_min) * random.random()
    yield env.timeout(duracion)
    print(f"\n💈 {tipo.replace('_', ' ').title()} terminado para {cliente} en {duracion:.2f} minutos.")
    tiempo_servicio_total += duracion


# ============================================================
# PROCESO DEL CLIENTE
# ============================================================

def atender_cliente(env, nombre, peluqueros):
    global tiempo_espera_total, tiempo_final
    llegada = env.now
    print(f"\n----> {nombre} llegó a la peluquería en el minuto {llegada:.2f}")

    with peluqueros.request() as turno:
        yield turno
        inicio = env.now
        espera = inicio - llegada
        tiempo_espera_total += espera
        print(f"{nombre} es atendido en el minuto {inicio:.2f} (esperó {espera:.2f} minutos)")

        tipo_servicio = random.choice(list(SERVICIOS.keys()))
        tiempo_min, tiempo_max = SERVICIOS[tipo_servicio]
        yield env.process(servicio(env, nombre, tipo_servicio, tiempo_min, tiempo_max))

        salida = env.now
        print(f"<---- {nombre} sale de la peluquería en el minuto {salida:.2f}")
        tiempo_final = salida


# ============================================================
# GENERADOR DE CLIENTES
# ============================================================

def generador_clientes(env, peluqueros):
    for i in range(1, TOTAL_CLIENTES + 1):
        tiempo_entre_llegadas = -TIEMPO_LLEGADA_MEDIA * math.log(random.random())
        yield env.timeout(tiempo_entre_llegadas)
        env.process(atender_cliente(env, f"Cliente {i}", peluqueros))


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    print("------------------ SIMULACIÓN PELUQUERÍA ------------------")
    random.seed(SEMILLA)
    
    env = simpy.Environment()
    peluqueros = simpy.Resource(env, capacity=NUMERO_PELUQUEROS)
    env.process(generador_clientes(env, peluqueros))
    env.run()

    # Resultados
    print("\n**************** FIN DE JORNADA LABORAL ****************")
    print(f"\nTotal clientes atendidos: {TOTAL_CLIENTES}")
    print(f"Horas simuladas: {tiempo_final / 60:.2f} hrs\n")

    print("Indicadores obtenidos:")
    longitud_promedio_cola = tiempo_espera_total / tiempo_final
    tiempo_espera_promedio = tiempo_espera_total / TOTAL_CLIENTES
    print(f"Longitud promedio de la cola: {longitud_promedio_cola:.2f}")
    print(f"Tiempo de espera promedio: {tiempo_espera_promedio:.2f} minutos")


if __name__ == "__main__":
    main()
