import random
from js import Math, document

LETRAS = "ABCDEFGHIJKL"
n = 6
aristas = set()
seleccionado = None
componentes = []
componentes_calculadas = []
indice_componente = 0
matriz_caminos = []
pares_por_evaluar = []
indice_par = 0
fase_analisis = ""
pendientes = []
visitados = set()
componente_actual = []
paso_activo = False
reflexividad_mostrada = False
componente_por_nodo = {}
pasos_caminos = []
historial_caminos = []
indice_paso = 0

PALETA = [
    "#42c77a", "#4da3ff", "#c084fc", "#ff9f43",
    "#f05d7b", "#36cfc9", "#e5c453", "#f472d0",
    "#8bd450", "#9b8cff", "#ff785a", "#5bd1a8"
]


def clave(a, b):
    return (a, b)


def puntos_flecha(p1, p2, doble=False):
    # Extremos de la flecha p1 -> p2 (recortada al borde de los círculos).
    # Si existe también la flecha de regreso (doble), se desplaza hacia un lado
    # para que ambas queden paralelas y separadas, no una encima de otra.
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    distancia = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / distancia, dy / distancia
    if doble:
        ox, oy = -uy * 8, ux * 8
        x1, y1, x2, y2 = x1 + ox, y1 + oy, x2 + ox, y2 + oy
    return x1 + 25 * ux, y1 + 25 * uy, x2 - 29 * ux, y2 - 29 * uy


def vecinos(v):
    return sorted(set(
        [b for a, b in aristas if a == v] +
        [a for a, b in aristas if b == v]
    ))


def obtener_matriz_adyacencia():
    return [
        [1 if (i, j) in aristas else 0 for j in range(n)]
        for i in range(n)
    ]


def obtener_matriz_a_mas_i():
    A_I = obtener_matriz_adyacencia()
    for i in range(n):
        A_I[i][i] = 1  
    return A_I


def calcular_matriz_caminos():
    M = obtener_matriz_a_mas_i()
    pasos = []
    for i in range(n):
        cambio = True
        while cambio:
            cambio = False
            for k in range(n):
                if k == i or not M[i][k]:
                    continue
                nuevos = [j for j in range(n) if M[k][j] and not M[i][j]]
                if nuevos:
                    for j in nuevos:
                        M[i][j] = 1
                    pasos.append({"fila": i, "pivote": k, "nuevos": nuevos,
                                  "matriz": [f[:] for f in M]})
                    cambio = True
    return pasos, M


def calcular_componentes(caminos):
    orden = ordenar_filas(caminos)
    bloques = []
    p = 0
    while p < len(orden):
        q = p + 1
        while (q < len(orden)
               and caminos[orden[p]][orden[q]] == 1
               and caminos[orden[q]][orden[p]] == 1):
            q += 1
        bloques.append(sorted(orden[p:q]))
        p = q
    return bloques


def ordenar_filas(caminos):
    def clave_orden(i):
        fila = caminos[i]
        primer_uno = fila.index(1) if 1 in fila else len(fila)
        return (-sum(fila), primer_uno, [-v for v in fila], i)

    return sorted(range(len(caminos)), key=clave_orden)


def mostrar_pasos_iniciales():
    el = document.getElementById("introSteps")
    if el is None:
        return
    pasos = [
        "Construir la matriz de adyacencia A del grafo.",
        "Agregar 1 en la diagonal principal: se obtiene A + I.",
        "Calcular la matriz de caminos a partir de A + I (solo indica si se puede ir de un vértice a otro).",
        "Contar los 1 de cada fila y ordenar las filas de mayor a menor (empate: el 1 más cercano a la primera columna).",
        "Ordenar las columnas en el mismo orden que las filas y mostrar la matriz ordenada.",
        "Identificar las componentes conexas en los bloques diagonales de unos de la matriz ordenada.",
        "Mostrar las componentes conexas encontradas y sus subgrafos.",
    ]
    el.innerHTML = "".join(f"<li>{p}</li>" for p in pasos)


def tabla_caminos(m, paso=None):
    fila = paso["fila"] if paso else -1
    pivote = paso["pivote"] if paso else -1
    nuevos = paso["nuevos"] if paso else []
    html = '<table class="matrix reach-matrix"><tr><th></th>'
    for j in range(n):
        marca = ' style="outline:2px solid #ffb000;border-radius:50%"' if j == pivote else ""
        html += f"<th{marca}>{LETRAS[j]}</th>"
    html += "</tr>"
    for i in range(n):
        flecha = "➜ " if i == fila else ""
        html += f"<tr><th>{flecha}{LETRAS[i]}</th>"
        for j in range(n):
            clase = "diagonal" if i == j else ("reachable-cell" if m[i][j] else "unreachable-cell")
            estilo = ""
            if i == fila and j in nuevos:
                estilo = "color:#ff5a5a;font-weight:800;"
            if i == pivote:
                estilo += "box-shadow:inset 0 0 0 1px #ffb000;"
            estilo = f' style="{estilo}"' if estilo else ""
            html += f'<td class="{clase}"{estilo}>{m[i][j]}</td>'
        html += "</tr>"
    return html + "</table>"


def mostrar_matriz_caminos(m=None, paso=None, titulo=""):
    m = m if m is not None else matriz_caminos
    document.getElementById("pathmatrix").innerHTML = tabla_caminos(m, paso)


def mostrar_matriz_ordenada(visibles=0):
    # visibles = cuantas componentes ya se "leyeron" (solo ellas llevan borde de color)
    componente_de = {}
    for indice, grupo in enumerate(componentes_calculadas[:visibles]):
        for nodo in grupo:
            componente_de[nodo] = indice

    orden = ordenar_filas(matriz_caminos)
    document.getElementById("matrixOrder").textContent = (
        "Orden de filas y columnas: " + ", ".join(LETRAS[v] for v in orden)
    )
    posiciones = {}
    for pos, nodo in enumerate(orden):
        if nodo in componente_de:
            posiciones.setdefault(componente_de[nodo], []).append(pos)

    html = '<table class="matrix ordered-matrix"><tr><th></th>'
    html += "".join(f"<th>{LETRAS[v]}</th>" for v in orden) + "</tr>"
    for fila_pos, origen in enumerate(orden):
        html += f"<tr><th>{LETRAS[origen]}</th>"
        for col_pos, destino in enumerate(orden):
            valor = matriz_caminos[origen][destino]
            clase = "ordered-one" if valor else "ordered-zero"
            estilo = ""
            idc = componente_de.get(origen)
            if idc is not None and idc == componente_de.get(destino):
                inicio, fin = min(posiciones[idc]), max(posiciones[idc])
                clase += " component-block"
                if fila_pos == inicio:
                    clase += " block-top"
                if fila_pos == fin:
                    clase += " block-bottom"
                if col_pos == inicio:
                    clase += " block-left"
                if col_pos == fin:
                    clase += " block-right"
                estilo = f' style="--block-color:{PALETA[idc % len(PALETA)]}"'
            html += f'<td class="{clase}"{estilo}>{valor}</td>'
        html += "</tr>"
    tabla = html + "</table>"
    document.getElementById("orderedMatrix").innerHTML = tabla


def mostrar_matriz(contenedor_id, matriz):
    resaltar = contenedor_id == "adjIdentityMatrix"
    html = '<table class="matrix"><tr><th></th>'
    html += "".join(f"<th>{LETRAS[j]}</th>" for j in range(n)) + "</tr>"
    for i, fila in enumerate(matriz):
        html += f"<tr><th>{LETRAS[i]}</th>"
        for j, valor in enumerate(fila):
            clase = "one" if valor else "zero"
            estilo = ""
            if resaltar and i == j and (i, j) not in aristas:
                estilo = ' style="outline:2px solid #ffb000"'  
            html += f'<td class="{clase}"{estilo}>{valor}</td>'
        html += "</tr>"
    document.getElementById(contenedor_id).innerHTML = html + "</table>"


def dibujar_grafo_reflexivo():
    svg = document.getElementById("reflexiveGraph")
    cx, cy, rx, ry = 370, 225, 310, 175
    puntos = [
        (cx + rx * Math.cos(-Math.PI / 2 + i * 2 * Math.PI / n),
         cy + ry * Math.sin(-Math.PI / 2 + i * 2 * Math.PI / n))
        for i in range(n)
    ]
    markup = (
        '<defs><marker id="arrowReflexive" markerWidth="10" markerHeight="10" '
        'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#ffb000" /></marker></defs>'
    )
    for a, b in sorted(aristas):
        x1, y1, x2, y2 = puntos_flecha(puntos[a], puntos[b], (b, a) in aristas)
        markup += (
            f'<line class="edge" marker-end="url(#arrowReflexive)" '
            f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'
        )
    for i, (x, y) in enumerate(puntos):
        markup += (
            f'<path fill="none" stroke="#ffb000" stroke-width="2" '
            f'd="M {x-10},{y-22} C {x-30},{y-55} {x+30},{y-55} {x+10},{y-22}" '
            f'marker-end="url(#arrowReflexive)" />'
        )
    for i, (x, y) in enumerate(puntos):
        markup += (
            f'<g><circle cx="{x}" cy="{y}" r="25" fill="#211707" '
            f'stroke="#ffb000" stroke-width="2" />'
            f'<text class="nlabel" x="{x}" y="{y}">{LETRAS[i]}</text></g>'
        )
    svg.innerHTML = markup


def dibujar(event=None):
    global seleccionado

    svg = document.getElementById("graph")
    cx, cy, rx, ry = 370, 225, 310, 175
    puntos = []

    for i in range(n):
        ang = -Math.PI / 2 + i * 2 * Math.PI / n
        puntos.append((
            cx + rx * Math.cos(ang),
            cy + ry * Math.sin(ang)
        ))

    markup = (
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" '
        'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#ffb000" />'
        '</marker></defs>'
    )

    for a, b in sorted(aristas):
        x1, y1, x2, y2 = puntos_flecha(puntos[a], puntos[b], (b, a) in aristas)

        markup += (
            f'<line class="edge" '
            f'marker-end="url(#arrow)" data-a="{a}" data-b="{b}" '
            f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'
        )

    for i, (x, y) in enumerate(puntos):
        css = "node chosen" if seleccionado == i else "node"
        markup += (
            f'<g data-v="{i}">'
            f'<circle class="{css}" cx="{x}" cy="{y}" r="25"/>'
            f'<text class="nlabel" x="{x}" y="{y}">{LETRAS[i]}</text>'
            f'</g>'
        )

    svg.innerHTML = markup

    for grupo in svg.querySelectorAll("[data-v]"):
        def evento_nodo(el):
            def click(event):
                global seleccionado

                v = int(el.dataset.v)
                if paso_activo:
                    return

                if seleccionado is None:
                    seleccionado = v
                    document.getElementById("graphmsg").textContent = (
                        f"{LETRAS[v]} seleccionado. "
                        "Elige el otro vértice para crear la conexión."
                    )
                elif seleccionado == v:
                    seleccionado = None
                    document.getElementById("graphmsg").textContent = (
                        "Selección cancelada."
                    )
                else:
                    e = clave(seleccionado, v)
                    inversa = clave(v, seleccionado)

                    if e in aristas:
                        aristas.remove(e)
                        document.getElementById("graphmsg").textContent = (
                            f"Flecha {LETRAS[e[0]]} → {LETRAS[e[1]]} eliminada."
                        )
                    elif inversa in aristas:
                        aristas.add(e)
                        document.getElementById("graphmsg").textContent = (
                            f"Conexión {LETRAS[seleccionado]} ↔ {LETRAS[v]} ahora es bidireccional."
                        )
                    else:
                        aristas.add(e)
                        document.getElementById("graphmsg").textContent = (
                            f"Se agregó la conexión {LETRAS[seleccionado]} → {LETRAS[v]}. "
                            "Si quieres, puedes agregar también la conexión de regreso."
                        )

                    seleccionado = None

                dibujar()

            return click

        grupo.onclick = evento_nodo(grupo)

    for linea in svg.querySelectorAll("line"):
        def evento_linea(el):
            def click(event):
                if paso_activo:
                    return

                aristas.discard((
                    int(el.dataset.a),
                    int(el.dataset.b)
                ))
                dibujar()

            return click

        linea.onclick = evento_linea(linea)

    # La matriz A se actualiza en tiempo real; A + I se revela con el botón.
    mostrar_matriz("adjMatrix", obtener_matriz_adyacencia())
    mostrar_matriz("adjIdentityMatrix", obtener_matriz_a_mas_i())
    dibujar_grafo_reflexivo()


def avanzar_inicio(event):
    global reflexividad_mostrada

    if not reflexividad_mostrada:
        document.getElementById("step1Matrices").classList.remove("hidden")
        document.getElementById("startWalk").textContent = (
            "Continuar al punto 2 · Matrices y revisión"
        )
        reflexividad_mostrada = True
        document.getElementById("step1Matrices").scrollIntoView(
            {"behavior": "smooth", "block": "center"}
        )
        return

    comenzar(event)


def reiniciar_paso_inicial():
    global reflexividad_mostrada
    reflexividad_mostrada = False
    document.getElementById("step1Matrices").classList.add("hidden")
    document.getElementById("startWalk").textContent = (
        "Mostrar A + I y grafo de la matriz A + I"
    )


def cambiar_tamano(event):
    global n, aristas, seleccionado, paso_activo, visitados

    n = int(document.getElementById("size").value)
    aristas = set()
    seleccionado = None
    paso_activo = False
    visitados = set()
    componente_por_nodo.clear()
    reiniciar_paso_inicial()

    document.getElementById("stepResult").classList.add("hidden")
    document.getElementById("stepSubgraphs").classList.add("hidden")
    document.getElementById("stepWalk").classList.add("hidden")
    document.getElementById("graphmsg").textContent = (
        "Grafo vacío. Haz clic en dos vértices para crear una flecha."
    )

    dibujar()


def generar_aleatorio(event):
    global aristas, seleccionado, paso_activo

    aristas = set()
    seleccionado = None
    paso_activo = False
    componente_por_nodo.clear()
    reiniciar_paso_inicial()

    for a in range(n):
        for b in range(a + 1, n):
            if random.random() < 0.24:
                aristas.add(
                    (a, b) if random.random() < 0.5 else (b, a)
                )

                if random.random() < 0.18:
                    if (a, b) in aristas:
                        aristas.add((b, a))
                    else:
                        aristas.add((a, b))

    document.getElementById("stepWalk").classList.add("hidden")
    document.getElementById("stepResult").classList.add("hidden")
    document.getElementById("stepSubgraphs").classList.add("hidden")
    document.getElementById("graphmsg").textContent = f"Grafo aleatorio generado con {len(aristas)} flechas."

    dibujar()


def limpiar(event):
    global aristas, seleccionado, paso_activo, visitados

    aristas = set()
    seleccionado = None
    paso_activo = False
    visitados = set()
    componente_por_nodo.clear()
    reiniciar_paso_inicial()

    document.getElementById("stepWalk").classList.add("hidden")
    document.getElementById("stepResult").classList.add("hidden")
    document.getElementById("stepSubgraphs").classList.add("hidden")
    document.getElementById("graphmsg").textContent = (
        "Grafo vacío. Haz clic en dos vértices para crear una flecha."
    )

    dibujar()


def comenzar(event):
    global componentes, componentes_calculadas, indice_componente
    global paso_activo, matriz_caminos, pasos_caminos, indice_paso, fase_analisis

    componentes = []
    componente_por_nodo.clear()
    pasos_caminos, matriz_caminos = calcular_matriz_caminos()
    componentes_calculadas = calcular_componentes(matriz_caminos)
    indice_componente = 0
    indice_paso = 0
    fase_analisis = "caminos"
    paso_activo = True

    document.getElementById("stepWalk").classList.remove("hidden")
    for ident in ("stepResult", "stepSubgraphs", "finalMatrixBox"):
        document.getElementById(ident).classList.add("hidden")
    document.getElementById("walkLog").innerHTML = (
        "<li><b>Matriz de partida A + I:</b> ya se agregaron los 1 de la diagonal; "
        "recién ahora se calcula la matriz de caminos.</li>"
    )
    document.getElementById("componentWalkLog").innerHTML = ""
    document.getElementById("sortingMessage").textContent = ""
    document.getElementById("componentState").textContent = ""
    document.getElementById("walkState").textContent = (
        "Se recorre fila por fila: si la fila i tiene un 1 en la columna k, "
        "la fila i se completa con los 1 de la fila k. La matriz de caminos solo "
        "indica si se puede ir de un vértice a otro."
    )
    document.getElementById("nextStep").disabled = False
    historial_caminos.clear()
    mostrar_matriz_caminos(obtener_matriz_a_mas_i(), titulo="A + I (matriz de partida)")
    dibujar()
    document.getElementById("stepWalk").scrollIntoView({"behavior": "smooth", "block": "start"})


def siguiente_paso(event):
    global indice_paso, indice_componente, fase_analisis, paso_activo
    log = document.getElementById("walkLog")
    estado = document.getElementById("walkState")

    if fase_analisis == "caminos":
        if indice_paso < len(pasos_caminos):
            p = pasos_caminos[indice_paso]
            indice_paso += 1
            f, k = LETRAS[p["fila"]], LETRAS[p["pivote"]]
            cols = ", ".join(LETRAS[j] for j in p["nuevos"])
            mostrar_matriz_caminos(p["matriz"], p, f"Paso {indice_paso}: fila {f} = fila {f} ∪ fila {k}")
            log.innerHTML += (
                f"<li><b>Fila {f}, columna {k}:</b> hay un 1 en ({f}, {k}), entonces "
                f"fila {f} = fila {f} ∪ fila {k}. Nuevos 1 en: {cols}.</li>"
            )
            estado.textContent = f"Paso {indice_paso} de {len(pasos_caminos)}."
            return
        mostrar_matriz_caminos(matriz_caminos, titulo="M_R∞: matriz de caminos")
        log.innerHTML += (
            "<li>Ninguna fila cambia más: esta es la matriz de caminos M<sub>R∞</sub>. "
            "Un 1 en (X, Y) indica que se puede ir de X a Y.</li>"
        )
        estado.textContent = "Matriz de caminos lista. Ahora se ordenarán sus filas y columnas."
        fase_analisis = "ordenar"
        return

    if fase_analisis == "ordenar":
        mostrar_matriz_ordenada(0)
        document.getElementById("finalMatrixBox").classList.remove("hidden")
        document.getElementById("sortingMessage").textContent = (
            "Se ordenaron las filas de mayor a menor cantidad de 1 "
            "(empate: el 1 más cercano a la primera columna) y las columnas en el mismo orden."
        )
        document.getElementById("componentState").textContent = (
            "Ahora se identifican las componentes conexas en los bloques diagonales de unos."
        )
        fase_analisis = "bloques"
        return

    if indice_componente < len(componentes_calculadas):
        grupo = componentes_calculadas[indice_componente]
        componentes.append(grupo[:])
        nombres = ", ".join(LETRAS[v] for v in grupo)
        indice_componente += 1
        mostrar_matriz_ordenada(indice_componente)
        document.getElementById("componentWalkLog").innerHTML += (
            f"<li><b>Componente conexa {indice_componente}:</b> {nombres} "
            "(bloque diagonal de unos).</li>"
        )
        document.getElementById("componentState").textContent = (
            f"Bloque {indice_componente}: {nombres}."
        )
        if indice_componente >= len(componentes_calculadas):
            paso_activo = False
            terminar()


def mostrar_subgrafos():
    cantidad = len(componentes)
    posiciones = {}
    colores_nodo = {}
    svg = (
        '<defs>'
        + ''.join(
            f'<marker id="arrowComp{i}" markerWidth="10" markerHeight="10" '
            f'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">'
            f'<path d="M0,0 L0,6 L9,3 z" fill="{PALETA[i % len(PALETA)]}" />'
            f'</marker>' for i in range(cantidad)
        )
        + '</defs>'
    )

    cx, cy, radio_x, radio_y = 370, 225, 310, 175
    for nodo in range(n):
        ang = -Math.PI / 2 + nodo * 2 * Math.PI / n
        posiciones[nodo] = (
            cx + radio_x * Math.cos(ang),
            cy + radio_y * Math.sin(ang)
        )

    for indice, grupo in enumerate(componentes):
        color = PALETA[indice % len(PALETA)]
        for nodo in grupo:
            colores_nodo[nodo] = color

    for indice, grupo in enumerate(componentes):
        for a, b in sorted(aristas):
            if a not in grupo or b not in grupo:
                continue
            x1, y1, x2, y2 = puntos_flecha(posiciones[a], posiciones[b], (b, a) in aristas)
            color = PALETA[indice % len(PALETA)]
            svg += (
                f'<line class="component-edge" stroke="{color}" '
                f'marker-end="url(#arrowComp{indice})" '
                f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'
            )

    for nodo, (x, y) in posiciones.items():
        color = colores_nodo[nodo]
        svg += (
            f'<g><circle cx="{x}" cy="{y}" r="25" fill="{color}" '
            f'stroke="#f1e7d5" stroke-width="2" />'
            f'<text class="nlabel" x="{x}" y="{y}">{LETRAS[nodo]}</text></g>'
        )

    document.getElementById("componentGraph").innerHTML = svg
    document.getElementById("componentLegend").innerHTML = "".join(
        f'<span class="legend-item" style="--component-color:{PALETA[i % len(PALETA)]}">'
        f'<i></i>Componente conexa {i + 1}: '
        f'{", ".join(LETRAS[v] for v in grupo)}</span>'
        for i, grupo in enumerate(componentes)
    )


def terminar():
    document.getElementById("nextStep").disabled = True
    document.getElementById("stepResult").classList.remove("hidden")
    document.getElementById("stepSubgraphs").classList.remove("hidden")
    document.getElementById("componentCount").textContent = str(len(componentes))
    document.getElementById("componentList").innerHTML = "".join(
        f'<li style="--component-color:{PALETA[i % len(PALETA)]}">'
        f'<span class="swatch"></span>Componente conexa {i + 1}: '
        f'{", ".join(LETRAS[v] for v in comp)}</li>'
        for i, comp in enumerate(componentes)
    )
    mostrar_subgrafos()
    document.getElementById("graphmsg").textContent = (
        f"Análisis terminado: {len(componentes)} componentes conexas."
    )
    document.getElementById("stepResult").scrollIntoView({
        "behavior": "smooth", "block": "start"
    })


selector = document.getElementById("size")

for valor in range(4, 13):
    opt = document.createElement("option")
    opt.value = valor
    opt.textContent = valor
    selector.appendChild(opt)

selector.value = n
selector.onchange = cambiar_tamano
document.getElementById("randomGraph").onclick = generar_aleatorio
document.getElementById("clear").onclick = limpiar
document.getElementById("startWalk").onclick = avanzar_inicio
document.getElementById("nextStep").onclick = siguiente_paso

for tab in document.querySelectorAll(".tab"):
    def evento_tab(el):
        def click(event):
            panel = document.getElementById(el.dataset.panel)
            abierto = panel.classList.contains("open")

            for p in document.querySelectorAll(".tab-panel"):
                p.classList.remove("open")

            for t in document.querySelectorAll(".tab"):
                t.setAttribute("aria-expanded", "false")

            if not abierto:
                panel.classList.add("open")
                el.setAttribute("aria-expanded", "true")

        return click

    tab.onclick = evento_tab(tab)


mostrar_pasos_iniciales()
dibujar()
