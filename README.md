# vrp_vns_optimizer
Repositorio código entrega final trabajo de análisis de metaheurística para el ramo de optimización ICI4151-2 

Cesar Anabalo 21.587.124-k
Fabiana Piña 21.526.472-6
Francisca silva 21.571.001-7

Este proyecto implementa una solución para el **Problema de Enrutamiento de Vehículos con Capacidad (VRP)** utilizando la metaheurística de **Búsqueda de Vecindario Variable (VNS)**, específicamente la estrategia de Descenso de Vecindario Variable (VND). El CVRP busca optimizar las rutas de una flota de vehículos para atender a un conjunto de clientes con demandas específicas, minimizando la distancia total recorrida y respetando la capacidad de carga de cada vehículo.

La solución generada permite encontrar rutas eficientes para el transporte de mercancías o servicios, ideal para la logística y distribución.

### Características

* **Lectura de Archivos Estándar CVRP**: Compatible con formatos de archivo `.txt` o `.vrp` para la carga de instancias del problema.
* **Cálculo de Distancias Euclidianas**: Generación automática de la matriz de distancias entre todos los nodos.
* **Generación de Solución Inicial Greedy**: Punto de partida heurístico para la optimización.
* **Implementación de VNS con VND**: Utiliza una combinación de operadores de vecindario para explorar el espacio de soluciones:
    * **Relocate**: Mueve un cliente individual.
    * **Swap**: Intercambia dos clientes (intra o inter-ruta).
    * **2-Opt**: Invierte segmentos de ruta para optimizar la secuencia.
    * **Interchange**: Intercambia segmentos de clientes entre diferentes rutas.
* **Manejo Robustos de Soluciones**: Funciones de **`fix_solution`** y **`validate_solution`** para asegurar la factibilidad (no duplicados, clientes faltantes, etc.) y la validez de las rutas generadas en todo momento.
* **Salida Clara por Consola**: Muestra el progreso del algoritmo y los resultados de la solución inicial y final.

### Requisitos

* **Python**: El código ha sido desarrollado y probado en Python .
* **Ninguna librería externa adicional** es estrictamente necesaria fuera de las que vienen con la instalación estándar de Python (`math`, `random`, `re`, `collections`).

### Cómo Usar
1.  **Preparar el Archivo de Instancia CVRP**
    Asegúrate de tener un archivo de texto con la definición de tu problema CVRP (ej. `Medio.txt`, `A-n32-k5.vrp`) en la misma carpeta que el script de Python, o actualiza la ruta del archivo directamente en el script:
    ```python
    # En la sección 'if __name__ == "__main__":' del script:
    file_path = "Medio.txt"  # <--- Cambia esto si tu archivo tiene otro nombre o ruta
    ```

2.  **Ejecutar el Optimizador**
    Abre tu terminal o línea de comandos, navega hasta la carpeta donde guardaste el script y ejecuta:
    ```bash
    python vrp_vns_optimizer.py
    ```
    (Reemplaza `vrp_vns_optimizer.py` con el nombre de tu archivo si es diferente).

El programa imprimirá la solución inicial, el progreso de la optimización con VNS y la mejor solución final encontrada junto con su costo.



### Licencia

Este proyecto está licenciado bajo la **Licencia MIT**.

Copyright (c) [2025] [Pontificia Universidad Católica de Valparaíso]

Permiso por la presente concedido, de forma gratuita, a cualquier persona que obtenga una copia
de este software y la documentación asociada (el "Software"), para tratar
en el Software sin restricciones, incluyendo, sin limitación, los derechos
de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software, y para permitir que las personas a quienes se les proporcione el Software
hagan lo mismo, sujeto a las siguientes condiciones:

El aviso de copyright anterior y este aviso de permiso se incluirán en todas
las copias o partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O
IMPLÍCITA, INCLUIDAS, ENTRE OTRAS, LAS GARANTÍAS DE COMERCIABILIDAD,
IDONEIDAD PARA UN FIN PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS
AUTORES O TITULARES DE LOS DERECHOS DE AUTOR SERÁN RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑO U OTRO
TIPO DE RESPONSABILIDAD, YA SEA POR ACCIÓN CONTRACTUAL, AGRAVIO O DE OTRO TIPO, DERIVADA DE,
FUERA DE O EN RELACIÓN CON EL SOFTWARE O EL USO U OTRAS OPERACIONES EN EL
SOFTWARE.
