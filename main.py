

from js import document, Math
import json


LETRAS_DISPONIBLES = "ABCDEFGHIJKL" 
cantidad_vertices = 8                
aristas_activas = set()              
vertice_seleccionado = None          
matriz_adyacencia = []               
matriz_potencia = []                 
matriz_usuario = []              
nivel_potencia = 1                   
calculo_finalizado = False           

selector_tamano = document.getElementById("size")
for i in range(4, 13):
    opcion = document.createElement("option")
    opcion.value = i
    opcion.textContent = i
    selector_tamano.appendChild(opcion)
selector_tamano.value = cantidad_vertices


def obtener_clave_arista(vertice_1, vertice_2):
    if vertice_1 < vertice_2:
        return f"{vertice_1}-{vertice_2}"
    else:
        return f"{vertice_2}-{vertice_1}"

def generar_matriz_adyacencia():
    matriz = []
    for i in range(cantidad_vertices):
        fila = []
        for j in range(cantidad_vertices):
            hay_conexion = 1 if (i != j and obtener_clave_arista(i, j) in aristas_activas) else 0
            fila.append(hay_conexion)
        matriz.append(fila)
    return matriz

def multiplicar_matrices_booleanas(matriz_izquierda, matriz_derecha):
    resultado = []
    for i in range(cantidad_vertices):
        fila = []
        for j in range(cantidad_vertices):
            # Comprueba si hay al menos un camino intermedio 'k'
            existe_camino = any(matriz_izquierda[i][k] and matriz_derecha[k][j] for k in range(cantidad_vertices))
            fila.append(1 if existe_camino else 0)
        resultado.append(fila)
    return resultado

def verificar_matrices_iguales(matriz_uno, matriz_dos):
    for i in range(cantidad_vertices):
        for j in range(cantidad_vertices):
            if matriz_uno[i][j] != matriz_dos[i][j]:
                return False
    return True



def dibujar_grafo_en_svg(event=None):
    global vertice_seleccionado
    lienzo_svg = document.getElementById("graph")
    
    centro_x, centro_y, radio_x, radio_y = 260, 162, 210, 115
    coordenadas_puntos = []
    
    for i in range(cantidad_vertices):
        angulo = -Math.PI / 2 + i * 2 * Math.PI / cantidad_vertices
        x = centro_x + radio_x * Math.cos(angulo)
        y = centro_y + radio_y * Math.sin(angulo)
        coordenadas_puntos.append((x, y))
    
    codigo_svg = ""
    
    for arista in list(aristas_activas):
        partes = arista.split("-")
        a, b = int(partes[0]), int(partes[1])
        codigo_svg += f'<line class="edge" data-a="{a}" data-b="{b}" x1="{coordenadas_puntos[a][0]}" y1="{coordenadas_puntos[a][1]}" x2="{coordenadas_puntos[b][0]}" y2="{coordenadas_puntos[b][1]}"/>'
    
    for i, (x, y) in enumerate(coordenadas_puntos):
        clase_nodo = "node chosen" if vertice_seleccionado == i else "node"
        codigo_svg += f'<g data-v="{i}"><circle class="{clase_nodo}" cx="{x}" cy="{y}" r="19"/><text class="nlabel" x="{x}" y="{y}">{LETRAS_DISPONIBLES[i]}</text></g>'
    
    lienzo_svg.innerHTML = codigo_svg
    
    for grupo_nodo in lienzo_svg.querySelectorAll("[data-v]"):
        def crear_evento_nodo(nodo_elemento):
            def al_hacer_clic(event):
                global vertice_seleccionado
                indice_vertice = int(nodo_elemento.dataset.v)
                mensaje_estado = document.getElementById("graphmsg")
                
                if vertice_seleccionado is None:
                    vertice_seleccionado = indice_vertice
                    mensaje_estado.textContent = f"{LETRAS_DISPONIBLES[indice_vertice]} elegido. Selecciona otro vértice para unirlos."
                elif vertice_seleccionado == indice_vertice:
                    vertice_seleccionado = None
                    mensaje_estado.textContent = "Selección cancelada."
                else:
                    clave = obtener_clave_arista(vertice_seleccionado, indice_vertice)
                    if clave in aristas_activas:
                        aristas_activas.remove(clave)
                        mensaje_estado.textContent = f"Conexión {LETRAS_DISPONIBLES[vertice_seleccionado]}–{LETRAS_DISPONIBLES[indice_vertice]} eliminada."
                    else:
                        aristas_activas.add(clave)
                        mensaje_estado.textContent = f"Conexión {LETRAS_DISPONIBLES[vertice_seleccionado]}–{LETRAS_DISPONIBLES[indice_vertice]} agregada."
                    vertice_seleccionado = None
                dibujar_grafo_en_svg()
                actualizar_tabla_matriz_cruda()
            return al_hacer_clic
        grupo_nodo.onclick = crear_evento_nodo(grupo_nodo)

    for linea_arista in lienzo_svg.querySelectorAll("line"):
        def crear_evento_linea(linea_elemento):
            def al_hacer_clic(event):
                clave = obtener_clave_arista(int(linea_elemento.dataset.a), int(linea_elemento.dataset.b))
                if clave in aristas_activas:
                    aristas_activas.remove(clave)
                dibujar_grafo_en_svg()
                actualizar_tabla_matriz_cruda()
            return al_hacer_clic
        linea_arista.onclick = crear_evento_linea(linea_arista)


def construir_tabla_matriz(selector_destino, matriz_datos, es_editable=False, solo_diagonal=False):
    contenedor_destino = document.getElementById(selector_destino.replace("#", ""))
    
    # Construir cabecera con letras
    html_tabla = '<table class="matrix"><tr><th></th>'
    for j in range(cantidad_vertices):
        html_tabla += f'<th>{LETRAS_DISPONIBLES[j]}</th>'
    html_tabla += '</tr>'
    
    # Construir filas
    for i, fila in enumerate(matriz_datos):
        html_tabla += f'<tr><th>{LETRAS_DISPONIBLES[i]}</th>'
        for j, valor in enumerate(fila):
            es_uno = valor == 1
            clase_valor = "one" if es_uno else "zero"
            permite_clic = es_editable and (not solo_diagonal or i == j)
            clase_clic = " clickable" if permite_clic else ""
            atributos_datos = f' data-i="{i}" data-j="{j}"' if permite_clic else ''
            html_tabla += f'<td class="{clase_valor}{clase_clic}"{atributos_datos}>{valor}</td>'
        html_tabla += '</tr>'
    
    contenedor_destino.innerHTML = html_tabla + '</table>'
    
    if es_editable:
        for celda in contenedor_destino.querySelectorAll("[data-i]"):
            def crear_evento_celda(celda_elemento):
                def al_hacer_clic(event):
                    i = int(celda_elemento.dataset.i)
                    j = int(celda_elemento.dataset.j)
                    
                    if selector_destino == "#adjmatrix":
                        matriz_adyacencia[i][j] ^= 1  # Alterna 0 y 1 con XOR
                        nuevo_valor = matriz_adyacencia[i][j]
                    else:
                        matriz_usuario[i][j] ^= 1
                        nuevo_valor = matriz_usuario[i][j]
                    
                    celda_elemento.textContent = nuevo_valor
                    celda_elemento.className = f"{'one' if nuevo_valor == 1 else 'zero'} clickable"
                return al_hacer_clic
            celda.onclick = crear_evento_celda(celda)

def actualizar_tabla_matriz_cruda():
    construir_tabla_matriz("#rawmatrix", generar_matriz_adyacencia())

def desplazar_a_seccion(id_seccion):
    """Desplaza la vista suavemente hacia la sección deseada."""
    seccion = document.getElementById(id_seccion.replace("#", ""))
    seccion.classList.remove("hidden")
    seccion.scrollIntoView({"behavior": "smooth", "block": "start"})

def iniciar_proceso_multiplicacion():
    global matriz_adyacencia, matriz_potencia, nivel_potencia, calculo_finalizado
    
    for i in range(cantidad_vertices):
        matriz_adyacencia[i][i] = 1
        
    construir_tabla_matriz("#adjmatrix", matriz_adyacencia)
    matriz_potencia = [fila[:] for fila in matriz_adyacencia]
    nivel_potencia = 1
    calculo_finalizado = False
    
    document.getElementById("checkProduct").disabled = False
    document.getElementById("showProduct").disabled = False
    preparar_siguiente_producto()
    desplazar_a_seccion("#stepProduct")

def preparar_siguiente_producto():
    global matriz_usuario
    matriz_usuario = [[0 for _ in range(cantidad_vertices)] for _ in range(cantidad_vertices)]
    
    document.getElementById("productPrompt").textContent = f"Calcula A{nivel_potencia + 1} = A{nivel_potencia} × A. Pulsa una casilla para cambiar entre 0 y 1."
    document.getElementById("powerTitle").textContent = f"Matriz A{nivel_potencia}"
    document.getElementById("resultTitle").textContent = f"Tu resultado · A{nivel_potencia + 1}"
    
    construir_tabla_matriz("#powerMatrix", matriz_potencia)
    construir_tabla_matriz("#productMatrix", matriz_usuario, True)
    mostrar_mensaje_retroalimentacion("")

def mostrar_mensaje_retroalimentacion(texto, clase=""):
    caja_feedback = document.getElementById("feedback")
    caja_feedback.textContent = texto
    caja_feedback.className = "feedback " + clase

def verificar_resultado_usuario(revelar_respuesta=False):
    global matriz_potencia, nivel_potencia, calculo_finalizado, matriz_usuario
    matriz_esperada = multiplicar_matrices_booleanas(matriz_potencia, matriz_adyacencia)
    
    if revelar_respuesta:
        matriz_usuario = [fila[:] for fila in matriz_esperada]
        
    if not verificar_matrices_iguales(matriz_usuario, matriz_esperada):
        mostrar_mensaje_retroalimentacion("Hay casillas incorrectas. Revisa bien las filas y columnas.", "bad")
        return
        
    matriz_potencia = matriz_esperada
    nivel_potencia += 1
    
    if verificar_matrices_iguales(multiplicar_matrices_booleanas(matriz_potencia, matriz_adyacencia), matriz_potencia):
        calculo_finalizado = True
        document.getElementById("productPrompt").textContent = f"¡La matriz se estabilizó en A{nivel_potencia}! Ya no se agregan nuevas rutas."
        document.getElementById("powerTitle").textContent = f"Matriz de caminos A{nivel_potencia}"
        document.getElementById("resultTitle").textContent = f"A{nivel_potencia} × A"
        matriz_usuario = multiplicar_matrices_booleanas(matriz_potencia, matriz_adyacencia)
        construir_tabla_matriz("#powerMatrix", matriz_potencia)
        construir_tabla_matriz("#productMatrix", matriz_usuario)
        mostrar_mensaje_retroalimentacion("¡Excelente! Se encontraron todas las rutas y componentes conexas del grafo.", "good")
        document.getElementById("checkProduct").disabled = True
        document.getElementById("showProduct").disabled = True
        return
        
    preparar_siguiente_producto()
    mostrar_mensaje_retroalimentacion(f"¡Correcto! A{nivel_potencia} guardada con éxito. Continúa con la siguiente potencia.", "good")

def cambiar_tamano_grafo(event):
    global cantidad_vertices, aristas_activas, vertice_seleccionado
    cantidad_vertices = int(document.getElementById("size").value)
    aristas_activas.clear()
    vertice_seleccionado = None
    dibujar_grafo_en_svg()
    actualizar_tabla_matriz_cruda()

document.getElementById("size").onchange = cambiar_tamano_grafo

def limpiar_todo_grafo(event):
    global aristas_activas, vertice_seleccionado
    aristas_activas.clear()
    vertice_seleccionado = None
    dibujar_grafo_en_svg()
    actualizar_tabla_matriz_cruda()
    document.getElementById("graphmsg").textContent = "Grafo vacío. Haz clic en los nodos para conectarlos."

document.getElementById("clear").onclick = limpiar_todo_grafo

def cargar_grafo_ejemplo(event):
    global aristas_activas, vertice_seleccionado
    aristas_activas.clear()
    i = 0
    while i < cantidad_vertices:
        z = min(3, cantidad_vertices - i)
        if cantidad_vertices - i - z == 1:
            z -= 1
        grupo = list(range(i, i + z))
        for q in range(1, len(grupo)):
            aristas_activas.add(obtener_clave_arista(grupo[q - 1], grupo[q]))
        if len(grupo) == 3:
            aristas_activas.add(obtener_clave_arista(grupo[0], grupo[2]))
        i += z
    vertice_seleccionado = None
    dibujar_grafo_en_svg()
    actualizar_tabla_matriz_cruda()
    document.getElementById("graphmsg").textContent = "Grafo de ejemplo cargado. Puedes editar las conexiones."

document.getElementById("example").onclick = cargar_grafo_ejemplo

document.getElementById("nextMatrix").onclick = lambda e: (
    globals().update(matriz_adyacencia=generar_matriz_adyacencia()),
    construir_tabla_matriz("#adjmatrix", matriz_adyacencia, True, True),
    desplazar_a_seccion("#stepMatrix")
)

document.getElementById("backGraph").onclick = lambda e: document.getElementById("stepGraph").scrollIntoView({"behavior": "smooth"})

document.getElementById("nextProduct").onclick = lambda e: (
    mostrar_mensaje_retroalimentacion("Completa primero con 1 toda la diagonal principal.", "bad") if not all(matriz_adyacencia[i][i] == 1 for i in range(cantidad_vertices)) else iniciar_proceso_multiplicacion()
)

document.getElementById("backMatrix").onclick = lambda e: document.getElementById("stepMatrix").scrollIntoView({"behavior": "smooth"})
document.getElementById("checkProduct").onclick = lambda e: verificar_resultado_usuario(False)
document.getElementById("showProduct").onclick = lambda e: verificar_resultado_usuario(True)

# Control de las pestañas superiores de teoría/ayuda
for boton_pestana in document.querySelectorAll(".tab"):
    def crear_evento_pestana(pestana_elemento):
        def al_hacer_clic(event):
            panel_asociado = document.getElementById(pestana_elemento.dataset.panel)
            esta_abierto = panel_asociado.classList.contains("open")
            for panel in document.querySelectorAll(".tab-panel"):
                panel.classList.remove("open")
            for pestana in document.querySelectorAll(".tab"):
                pestana.setAttribute("aria-expanded", "false")
            if not esta_abierto:
                panel_asociado.classList.add("open")
                pestana_elemento.setAttribute("aria-expanded", "true")
        return al_hacer_clic
    boton_pestana.onclick = crear_evento_pestana(boton_pestana)

cargar_grafo_ejemplo(None)