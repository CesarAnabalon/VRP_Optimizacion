import math
import random
import re
import statistics
import matplotlib.pyplot as plt
from collections import Counter

# === Función para leer archivo CVRP tipo .txt o .vrp ===
def read_cvrp_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    dimension = 0
    capacity = 0
    coords = []
    demands = []
    depot = 0
    section = None

    for line in lines:
        line = line.strip()
        if "DIMENSION" in line:
            dimension = int(line.split(":")[1])
        elif "CAPACITY" in line:
            capacity = int(line.split(":")[1])
        elif line == "NODE_COORD_SECTION":
            section = "coords"
        elif line == "DEMAND_SECTION":
            section = "demands"
        elif line == "DEPOT_SECTION":
            section = "depot"
        elif line == "EOF":
            break
        elif section == "coords":
            parts = line.split()
            if len(parts) == 3:
                node = int(parts[0])
                x, y = int(parts[1]), int(parts[2])
                coords.append((x, y))
        elif section == "demands":
            parts = line.split()
            if len(parts) == 2:
                node = int(parts[0])
                demand = int(parts[1])
                demands.append(demand)
        elif section == "depot":
            val = int(line)
            if val != -1:
                depot = val - 1 # Convertir a índice 0-based

    return dimension, capacity, coords, demands, depot

d, cap, coords, demand, dep = read_cvrp_file("Dificil.txt")
print(d)
print(cap)
print(coords)
print(demand)
print(dep)

# === Calcular matriz de distancias euclidianas ===
def euclidean_distance_matrix(coords):
    n = len(coords)
    return [[math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1]) for j in range(n)] for i in range(n)]

# === Evaluar una solución ===
def calculate_cost(solucion, dist_matrix, demands, capacidad):
    costo_total = 0
    penalización = 0

    for ruta in solucion:
      if not ruta or ruta[0] != 0 or ruta[-1] != 0:
        penalización += 1000000 # Penalización muy alta para rutas fundamentalmente mal formadas
        continue
      if len(ruta) == 2 and ruta[0] == 0 and ruta[1] == 0:
        continue
      demanda_ruta = 0
      costo_ruta = 0

      for i in range(len(ruta)- 1):
        costo_ruta += dist_matrix[ruta[i]][ruta[i+1]]
        if ruta[i] != 0:
          demanda_ruta += demands[ruta[i]]

      costo_total += costo_ruta
      if demanda_ruta > capacidad:
        penalización += (demanda_ruta - capacidad) * 1000 # Penalización por exceso de capacidad

    return costo_total + penalización

# === Generar solución inicial greedy ===
def generate_initial_solution(demands, capacity):
    # Clientes son del 1 al N, el depósito es 0
    clientes = list(range(1, len(demands)))
    random.shuffle(clientes) #Se elige un cliente de forma aleatoria

    solucion = []
    ruta_actual = [0] # Empieza en el depósito
    carga_actual = 0

    for client_idx in range(len(clientes)):
        cliente = clientes[client_idx]

        if carga_actual + demands[cliente] <= capacity:
            ruta_actual.append(cliente)
            carga_actual += demands[cliente]
        else:
            ruta_actual.append(0)
            solucion.append(ruta_actual)
            ruta_actual = [0, cliente]
            carga_actual = demands[cliente]

    if len(ruta_actual) > 1:
        ruta_actual.append(0)
        solucion.append(ruta_actual)

    solucion_final = []
    for ruta in solucion:
        if len(ruta) > 2:
            solucion_final.append(ruta)
        elif len(ruta) == 2 and ruta[0] == 0 and ruta[1] == 0:
            pass

    if not solucion_final and len(demands) > 1:
        for cliente in clientes:
            solucion_final.append([0, cliente, 0])

    return solucion_final

# --- Operadores de Vecindario ---
# Operador 1: Relocate (Mover un cliente de una ruta a otra o dentro de la misma ruta)
def relocate(solucion, dist_matrix, demands, capacity):
    mejor_solucion = [r[:] for r in solucion]
    mejor_costo = calculate_cost(mejor_solucion, dist_matrix, demands, capacity)

    for i in range(len(solucion)):
      for j in range(1, len(solucion[i]) - 1):
        cliente_a_mover = solucion[i][j]

        for k in range(len(solucion)):
          for l in range(1, len(solucion[k]) + 1):
            if i==k and l == j:
              continue

            solucion_temp = [r[:] for r in solucion]
            solucion_temp[i].pop(j) #elimina al cliente de su posicion original
            if len(solucion_temp[i]) <= 1:
              solucion_temp[i] = [0, 0]

            solucion_temp[k].insert(l, cliente_a_mover)

            ruta_i = sum(demands[node] for node in solucion_temp[i] if node != 0)
            ruta_k = sum(demands[node] for node in solucion_temp[k] if node != 0)

            if ruta_i <= capacity and ruta_k <= capacity:
                        costo_actual = calculate_cost(solucion_temp, dist_matrix, demands, capacity)
                        if costo_actual < mejor_costo:
                            mejor_solucion = solucion_temp
                            mejor_costo = costo_actual

    return mejor_solucion

# Operador 2: Swap (Intercambiar dos clientes entre dos rutas diferentes o dentro de la misma ruta)
def swap(solucion, dist_matrix, demands, capacidad):
    mejor_solucion = [r[:] for r in solucion]
    mejor_costo = calculate_cost(mejor_solucion, dist_matrix, demands, capacidad)

    for r1_idx, ruta_1 in enumerate(solucion):
        for i in range(1, len(ruta_1) - 1):
            cliente_1 = ruta_1[i]

            for r2_idx, ruta_2 in enumerate(solucion):
                for j in range(1, len(ruta_2) - 1):
                    cliente_2 = ruta_2[j]

                    if r1_idx == r2_idx and i >= j:
                        continue

                    solucion_temp = [r[:] for r in solucion]

                    # Swap en la misma ruta
                    if r1_idx == r2_idx:
                        solucion_temp[r1_idx][i], solucion_temp [r1_idx][j] = solucion_temp[r1_idx][j], solucion_temp[r1_idx][i]
                    else: # Swap entre rutas diferentes
                        solucion_temp[r1_idx][i] = cliente_1
                        solucion_temp[r2_idx][j] = cliente_2

                    # Verificar validez de capacidad para las rutas modificadas
                    valid_swap = True
                    if r1_idx == r2_idx:
                        demandaRuta = sum(demands[node] for node in solucion_temp[r1_idx] if node != 0)
                        if demandaRuta > capacidad:
                            valid_swap = False
                    else:
                        demand_1 = sum(demands[node] for node in solucion_temp[r1_idx] if node != 0)
                        demand_2 = sum(demands[node] for node in solucion_temp[r2_idx] if node != 0)
                        if demand_1 > capacidad or demand_2 > capacidad:
                            valid_swap = False

                    if valid_swap:
                        costoActual = calculate_cost(solucion_temp, dist_matrix, demands, capacidad)
                        if costoActual < mejor_costo:
                            mejor_solucion = solucion_temp
                            mejor_costo = costoActual

    return mejor_solucion

# Operador 3: 2-Opt (Invertir un segmento de ruta para eliminar cruces)
def two_opt(solucion, dist_matrix, demands, capacidad):
    mejor_solucion = [r[:] for r in solucion]
    mejor_costo = calculate_cost(mejor_solucion, dist_matrix, demands, capacidad)

    for r_idx, ruta in enumerate(solucion):
        if len(ruta) < 4:
            continue

        for i in range(1, len(ruta) - 2): # Primer punto de corte
            for j in range(i + 1, len(ruta) - 1): # Segundo punto de corte

                # Crear la nueva ruta 2-opt
                # Segmento 1: desde el inicio hasta i-1
                # Segmento 2: desde j hasta i (invertido)
                # Segmento 3: desde j+1 hasta el final
                nuevaRuta = ruta[:i] + ruta[j:i-1:-1] + ruta[j+1:]

                solucion_temp = [r[:] for r in solucion]
                solucion_temp[r_idx] = nuevaRuta

                # Para 2-opt, la capacidad de la ruta no cambia, solo el orden, así que no se revisa explícitamente
                costo_actual = calculate_cost(solucion_temp, dist_matrix, demands, capacidad)
                if costo_actual < mejor_costo:
                  mejor_solucion = solucion_temp
                  mejor_costo = costo_actual

    return mejor_solucion

# Operador 4: Interchange (Intercambiar dos segmentos de ruta entre dos rutas diferentes)
def interchange(solucion, dist_matrix, demands, capacidad):
    mejor_solucion = [r[:] for r in solucion]
    mejor_costo = calculate_cost(mejor_solucion, dist_matrix, demands, capacidad)

    # Iterar sobre pares de rutas
    for r1_idx in range(len(solucion)):
        for r2_idx in range(r1_idx + 1, len(solucion)):
            ruta_1 = solucion[r1_idx]
            ruta_2 = solucion[r2_idx]

            nodo_1 = ruta_1[1:-1]
            nodo_2 = ruta_2[1:-1]

            if not nodo_1 or not nodo_2:
                continue

            # Iterar sobre todos los posibles puntos de corte en ambas rutas
            for i in range(len(nodo_1) + 1):
                for j in range(len(nodo_2) + 1):

                    # Dividir las rutas en segmentos basados en los puntos de corte
                    segUno_mitadUno = nodo_1[:i]
                    segUno_mitadDos = nodo_1[i:]

                    segDos_mitadUno = nodo_2[:i]
                    segDos_mitadDos = nodo_2[i:]

                    # Probar el intercambio de las segundas partes: (A1, B2) y (A2, B1)
                    nuevaRuta_uno = segUno_mitadUno + segDos_mitadDos
                    nuevaRuta_dos = segDos_mitadUno + segUno_mitadDos

                    temp_rutaUno = [0] + nuevaRuta_uno + [0]
                    temp_rutaDos = [0] + nuevaRuta_dos + [0]

                    # Verificar validez de capacidad para las nuevas rutas
                    demand_r1 = sum(demands[node] for node in temp_rutaUno if node != 0)
                    demand_r2 = sum(demands[node] for node in temp_rutaDos if node != 0)

                    if demand_r1 <= capacidad and demand_r2 <= capacidad:
                        solucion_temp = [r[:] for r in solucion]
                        solucion_temp[r1_idx] = temp_rutaUno
                        solucion_temp[r2_idx] = temp_rutaDos

                        costo_actual = calculate_cost(solucion_temp, dist_matrix, demands, capacidad)
                        if costo_actual < mejor_costo:
                          mejor_solucion = solucion_temp
                          mejor_costo = costo_actual

    return mejor_solucion
def fix_solution(solucion, num_clientes, demands, capacidad):
    # Paso 1: Limpiar y normalizar las rutas (asegurar [0, ..., 0] y eliminar rutas vacías)
    cleaned_solution = []
    all_nodes_present = [] # Para rastrear todos los clientes encontrados

    for ruta in solucion:
        # Asegurarse que la ruta comienza y termina en 0
        if not ruta or ruta[0] != 0:
            ruta.insert(0, 0)
        if not ruta or ruta[-1] != 0:
            ruta.append(0)

        # Eliminar depósitos consecutivos (ej. [0,0,cliente,0] a [0,cliente,0])
        temp_cleaned_route = []
        for i in range(len(ruta)):
            if i > 0 and ruta[i] == 0 and temp_cleaned_route[-1] == 0:
                continue
            temp_cleaned_route.append(ruta[i])

        # Si la ruta tiene clientes (más de 2 nodos [0,0]), la añadimos
        if len(temp_cleaned_route) > 2:
            cleaned_solution.append(temp_cleaned_route)
            for node in temp_cleaned_route:
                if node != 0:
                    all_nodes_present.append(node)
        elif len(temp_cleaned_route) == 2 and temp_cleaned_route[0] == 0 and temp_cleaned_route[1] == 0:
            pass

    # Paso 2: Identificar clientes duplicados y faltantes
    expected_customers = set(range(1, num_customers + 1))
    node_counts = Counter(all_nodes_present)

    current_found_customers_set = set(node_counts.keys())

    customers_to_remove_duplicates_of = {node for node, count in node_counts.items() if count > 1}

    # Crear la solución final eliminando los duplicados
    solution_without_duplicates = []
    for ruta in cleaned_solution:
        ruta_temp = [0] # Siempre empieza con el depósito
        visitados = set()

        for node in ruta[1:-1]: # Iterar sobre los clientes de la ruta (excluyendo depósitos)
            if node in customers_to_remove_duplicates_of and node in current_found_customers_set:
                if node_counts[node] > 0:
                    if node not in visitados:
                        ruta_temp.append(node)
                        visitados.add(node)
                        node_counts[node] -= 1
                    else:
                        pass
                else:
                    pass
            else:
                ruta_temp.append(node)
                visitados.add(node)

        ruta_temp.append(0) # Siempre termina con el depósito
        if len(ruta_temp) > 2: # Solo añadir rutas que tienen clientes
            solution_without_duplicates.append(ruta_temp)

    # Recalcular los clientes faltantes después de la eliminación de duplicados
    all_nodes_after_dup_fix = []
    for ruta in solution_without_duplicates:
        for node in ruta:
            if node != 0:
                all_nodes_after_dup_fix.append(node)

    found_customers_after_fix_set = set(all_nodes_after_dup_fix)
    missing_customers = list(expected_customers - found_customers_after_fix_set)

    # Paso 3: Reinsertar clientes faltantes y verificar capacidad final
    solucion_final = [r[:] for r in solution_without_duplicates]

    for cliente in missing_customers:
        inserted = False
        for ruta_idx, ruta in enumerate(solucion_final):
            current_load = sum(demands[node] for node in ruta if node != 0)
            if current_load + demands[cliente] <= capacidad:
                # Insertar antes del depósito final
                solucion_final[ruta_idx].insert(len(solucion_final[ruta_idx]) - 1, cliente)
                inserted = True
                break

        if not inserted:
            solucion_final.append([0, cliente, 0])

    # Paso 4: Eliminar rutas vacías resultantes ([0,0]) y asegurar unicidad
    final_cleaned_solution = []
    unique_route_tuples = set()
    for ruta in solucion_final:
        if len(ruta) > 2: # Solo añadir rutas que contengan al menos un cliente
            route_tuple = tuple(ruta)
            if route_tuple not in unique_route_tuples:
                final_cleaned_solution.append(ruta)
                unique_route_tuples.add(route_tuple)
        elif len(ruta) == 2 and ruta[0] == 0 and ruta[1] == 0:
             pass

    if not final_cleaned_solution and num_clientes > 0:
        for cliente in expected_customers:
            final_cleaned_solution.append([0, cliente, 0])


    return final_cleaned_solution
def validate_solution(solucion, num_clientes, demands, capacidad):
    all_nodes = []
    total_clientes = 0

    for ruta_idx, ruta in enumerate(solucion):
        if not ruta or ruta[0] != 0 or ruta[-1] != 0:
            print(f" Error de formato en Ruta #{ruta_idx+1}: {ruta} (no empieza/termina en depósito).")
            return False

        demandaRuta = 0
        nodes_in_route = []
        for i in range(len(ruta)):
            node = ruta[i]
            if node != 0:
                demandaRuta += demands[node]
                all_nodes.append(node)
                nodes_in_route.append(node)
                total_clientes += 1

        if demandaRuta > capacidad:
            print(f" Error de capacidad en Ruta #{ruta_idx+1}: {ruta} (Demanda: {demandaRuta}, Capacidad: {capacidad}).")
            return False

    # Validar que todos los clientes esperados están presentes y no hay duplicados
    clientes_esperados = set(range(1, num_clientes + 1))
    clientes_actuales = set(all_nodes)

    if clientes_actuales != clientes_esperados:
        clientes_faltantes = clientes_esperados - clientes_actuales
        clientes_duplicados = clientes_actuales - clientes_esperados

        print(f" Inconsistencia en clientes: {len(clientes_actuales)} únicos encontrados, {num_clientes} esperados.")
        if clientes_faltantes:
            print(f"   Clientes faltantes: {sorted(list(clientes_faltantes))}")
        if clientes_duplicados:
            print(f"   Clientes duplicados o extra (solo la primera instancia se cuenta aquí): {sorted(list(clientes_duplicados))}")
        return False

    # Contar ocurrencias para asegurar que cada cliente aparece solo una vez
    node_counts = Counter(all_nodes)
    for node, count in node_counts.items():
        if count > 1:
            print(f" Cliente {node} aparece {count} veces (debería ser 1).")
            return False

    return True
# --- Variable Neighborhood Search Completo (con estrategia VND) ---
def variable_neighborhood_search(dist_matrix, demands, capacidad, max_iter=100, solucion_inicial=None):
    if solucion_inicial is None:
        solucion_actual = generate_initial_solution(demands, capacity)
    else:
        solucion_actual = [r[:] for r in solucion_inicial]

    # Asegurar que la solución inicial sea válida y consistente
    num_clientes = len(demands) - 1
    solucion_actual = fix_solution(solucion_actual, num_clientes, demands, capacidad)
    costo_actual = calculate_cost(solucion_actual, dist_matrix, demands, capacidad)

    # Definir los operadores de vecindario a usar
    neighborhood_operators = [
        relocate,
        swap,
        two_opt,
        interchange
    ]

    print(f"--- Iniciando VNS ---")
    print(f"Costo inicial de la solución: {costo_actual:.2f}")

    sol_global = [r[:] for r in solucion_actual]
    costo_global = costo_actual

    for iter_count in range(max_iter):

        # Estrategia de Descenso de Vecindario Variable (VND)
        k = 0
        while k < len(neighborhood_operators):
            operador = neighborhood_operators[k]

            # Aplicar el operador de vecindario (búsqueda local dentro de este vecindario)
            neighbor_sol = operador(solucion_actual, dist_matrix, demands, capacidad)

           # Reparación de la solución
            neighbor_sol = fix_solution(neighbor_sol, num_clientes, demands, capacidad)
            neighbor_cost = calculate_cost(neighbor_sol, dist_matrix, demands, capacidad)

            # Comprobar si se encontró una mejora
            if neighbor_cost < costo_actual:
                solucion_actual, costo_actual = neighbor_sol, neighbor_cost
                if costo_actual < costo_global:
                    sol_global, costo_global = [r[:] for r in solucion_actual], costo_actual
                k = 0
            else:
                # Pasar al siguiente operador de vecindario
                k += 1

        if (iter_count + 1) % 50 == 0 or iter_count == max_iter -1:
            print(f"--- Iteración {iter_count + 1}/{max_iter} ---")
            print(f"Mejor costo global hasta ahora: {costo_global:.2f}")
            print(f"Costo de la solución actual: {costo_actual:.2f}")
            print("-" * 20)

    print(f"--- VNS Finalizado ---")
    print(f"Mejor costo global encontrado por VNS: {costo_global:.2f}")
    return sol_global, costo_global
# === Ejecutar ===
if __name__ == "__main__":
    file_path = "Facil.txt"
    dimension, capacity, coords, demands, depot = read_cvrp_file(file_path)
    dist_matrix = euclidean_distance_matrix(coords)

    num_clientes = dimension - 1
    print("--- Generando Solución Inicial ---")
    sol_inicial = generate_initial_solution(demands, capacity)

    # Es crucial arreglar y validar la solución inicial antes de pasarla a VNS
    sol_inicial = fix_solution(sol_inicial, num_clientes, demands, capacity)
    costo_inicial = calculate_cost(sol_inicial, dist_matrix, demands, capacity)

    print("\nSolución Inicial:")
    ruta_num = 1
    for ruta in sol_inicial:
        if len(ruta) > 2: # Evitar mostrar rutas [0, 0]
            demanda_rutaAct = sum(demands[node] for node in ruta if node != 0)
            costo_rutAct = calculate_cost([ruta], dist_matrix, demands, capacity)
            print(f"Ruta #{ruta_num}: {ruta} ")
            ruta_num += 1
    print(f"  Costo Total de la Solución Inicial: {costo_inicial:.2f}")
    if validate_solution(sol_inicial, num_clientes, demands, capacity):
        print(" La Solución Inicial es VÁLIDA.")
    else:
        print(" La Solución Inicial no es Válida.")
    print("-" * 50)

    # Aplicar VNS desde la solución inicial

    sol_final, costo_final = variable_neighborhood_search(
        dist_matrix, demands, capacity, max_iter=200
    )

    # Asegurar la validez de la solución final
    sol_final = fix_solution(sol_final, num_clientes, demands, capacity)

    print("\n--- Mejor Solución Encontrada por VNS ---")
    ruta_num = 1
    for ruta in sol_final:
        if len(ruta) > 2: # Evitar mostrar rutas [0, 0]
            demanda_rutaAct = sum(demands[node] for node in ruta if node != 0)
            costo_rutaAct = calculate_cost([ruta], dist_matrix, demands, capacity)
            print(f"Ruta #{ruta_num}: {ruta}")
            ruta_num += 1
    print(f" Costo Final Mejorado: {costo_final:.2f}")
    if validate_solution(sol_final, num_clientes, demands, capacity):
        print(" La Solución Final es VÁLIDA.")
    else:
        print(" La solución Final no es Válida")
    print("-" * 50)