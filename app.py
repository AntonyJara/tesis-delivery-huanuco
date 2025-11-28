import streamlit as st
from streamlit_folium import st_folium
import folium
import osmnx as ox
import networkx as nx
import random
import copy

# --- 1. CONFIGURACIÓN DE LA PÁGINA (ESTILO TESIS) ---
st.set_page_config(
    page_title="Optimización Logística - UNHEVAL",
    page_icon="🧬",
    layout="wide"
)

# --- BARRA LATERAL (INFORMACIÓN DEL AUTOR) ---
with st.sidebar:
    st.image("https://4.bp.blogspot.com/-BrxJfbOdhBk/XL-S-M8NjfI/AAAAAAABO6c/zgmW3D0du3kdVwGihkIwu-Z2n3qJFS9bwCLcBGAs/s1600/universidad-nacional-hermilio-valdizan-logo.jpg", width=100)
    st.title("Aplicación de Algoritmos Genéticos para la Planificación Eficiente de Delivery Urbano en Huánuco")
    st.info("**Autor:** Jara Bernardo Antony")
    st.write("Universidad Nacional Hermilio Valdizán")
    st.write("Huánuco, Perú")
    st.divider()
    st.write("Este sistema utiliza **Inteligencia Artificial Evolutiva** para resolver problemas de logística urbana en grafos complejos.")

st.title("🧬 Optimización de Rutas de Delivery con Algoritmos Genéticos")
st.subheader("Aplicado a la topografía urbana de Huánuco")

# --- 2. CREACIÓN DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📘 Marco Teórico", "⚙️ ¿Cómo Funciona?", "🛵 Simulador en Vivo"])

# =========================================================
# PESTAÑA 1: TEORÍA (Explicación Académica)
# =========================================================
with tab1:
    st.markdown("""
    ### ¿Qué es un Algoritmo Genético (AG)?
    
    Los Algoritmos Genéticos son métodos de búsqueda y optimización inspirados en la **teoría de la evolución natural de Charles Darwin**. 
    
    En lugar de calcular todas las posibles combinaciones (lo cual sería imposible en problemas grandes), el algoritmo "evoluciona" una población de soluciones hacia la mejor opción posible.
    
    #### Los 4 Pilares del Algoritmo:
    1.  **🧬 Población Inicial:** Se crean muchas rutas al azar (individuos).
    2.  **💪 Selección (Fitness):** Se evalúa qué tan buena es cada ruta. En nuestro caso, la "Aptitud" es la distancia total (mientras menos distancia, mejor).
    3.  **💕 Cruce (Crossover):** Las mejores rutas combinan sus características para crear nuevas rutas.
    4.  **✨ Mutación:** De vez en cuando, se cambia el orden de un pedido al azar para explorar nuevas posibilidades y no estancarse.
    """)
    
    st.info("💡 **Dato Curioso:** Para 15 pedidos, existen más de **1.3 billones** de rutas posibles. Un AG encuentra una ruta óptima en segundos sin revisar todas.")

# =========================================================
# PESTAÑA 2: LA LÓGICA (Explicación Técnica)
# =========================================================
with tab2:
    st.markdown("""
    ### El Problema del Viajante de Comercio (TSP)
    
    El objetivo es encontrar la ruta más corta posible que permita visitar una lista de clientes y regresar al punto de origen.
    
    #### Metodología del Proyecto
    
    Para aplicar esto a la ciudad de **Huánuco**, utilizamos el siguiente flujo de datos:
    
    * **1. Digitalización:** Usamos `OSMnx` para convertir las calles de Huánuco, Amarilis y Pillco Marca en un **Grafo Matemático** donde las intersecciones son nodos y las calles son aristas con peso (distancia).
    * **2. Matriz de Costos:** Calculamos la distancia real (respetando sentidos de tránsito) entre todos los puntos seleccionados usando el algoritmo de *Dijkstra*.
    * **3. Evolución:** * Creamos 100 rutas aleatorias.
        * Hacemos competir a las rutas durante 200 generaciones.
        * Aplicamos elitismo (las mejores 20 rutas sobreviven siempre).
    * **4. Visualización:** Renderizamos la solución final sobre un mapa interactivo.
    """)
    
    # Ecuación matemática (se ve muy bien en tesis)
    st.latex(r'''
    Fitness(x) = \sum_{i=0}^{n-1} Distancia(Punto_i, Punto_{i+1}) + Distancia(Punto_n, Punto_0)
    ''')

# =========================================================
# PESTAÑA 3: EL SIMULADOR (Tu código anterior)
# =========================================================
with tab3:
    st.write("### 📍 Panel de Control Interactivo")
    st.markdown("Selecciona el **Depósito** y los **Clientes** en el mapa para calcular la ruta óptima en tiempo real.")

    # --- CARGA DE DATOS ---
    @st.cache_resource
    def cargar_grafo():
        archivo = "huanuco.graphml"
        if not os.path.exists(archivo):
            st.error(f"No se encontró {archivo}. ¡Ejecuta mapa_huanuco.py primero!")
            return None
        G = ox.load_graphml(filepath=archivo)
        return G

    # Pequeña función auxiliar para verificar archivo
    import os
    
    G = cargar_grafo()

    if G:
        # GESTIÓN DEL ESTADO
        if 'puntos_seleccionados' not in st.session_state:
            st.session_state['puntos_seleccionados'] = []
        if 'ruta_calculada' not in st.session_state:
            st.session_state['ruta_calculada'] = None

        # LAYOUT DEL SIMULADOR
        col_mapa, col_datos = st.columns([3, 1])

        with col_mapa:
            # Mapa base
            m = folium.Map(location=[-9.9306, -76.2423], zoom_start=14, tiles="CartoDB positron")

            # Dibujar Puntos
            for i, coords in enumerate(st.session_state['puntos_seleccionados']):
                if i == 0:
                    folium.Marker(coords, popup="Depósito", icon=folium.Icon(color='green', icon='industry', prefix='fa')).add_to(m)
                else:
                    folium.Marker(coords, popup=f"Cliente {i}", icon=folium.Icon(color='blue', icon='truck', prefix='fa')).add_to(m)

            # Dibujar Ruta
            if st.session_state['ruta_calculada']:
                folium.PolyLine(st.session_state['ruta_calculada'], color="red", weight=5, opacity=0.8).add_to(m)

            output = st_folium(m, width=700, height=500)

        # Lógica de Clics
        if output['last_clicked']:
            punto = (output['last_clicked']['lat'], output['last_clicked']['lng'])
            if not st.session_state['puntos_seleccionados'] or st.session_state['puntos_seleccionados'][-1] != punto:
                st.session_state['puntos_seleccionados'].append(punto)
                st.session_state['ruta_calculada'] = None
                st.rerun()

        with col_datos:
            st.success(f"**Puntos seleccionados:** {len(st.session_state['puntos_seleccionados'])}")
            
            if st.button("🗑️ Limpiar Mapa"):
                st.session_state['puntos_seleccionados'] = []
                st.session_state['ruta_calculada'] = None
                st.rerun()
            
            if len(st.session_state['puntos_seleccionados']) >= 2:
                if st.button("🚀 Optimizar Ruta"):
                    with st.spinner("Evolucionando soluciones..."):
                        # 1. Preparar Nodos
                        coords = st.session_state['puntos_seleccionados']
                        nodos = [ox.nearest_nodes(G, Y=p[0], X=p[1]) for p in coords]
                        
                        # 2. Calcular Matriz
                        matriz = []
                        for o in nodos:
                            fila = []
                            for d in nodos:
                                try:
                                    dist = nx.shortest_path_length(G, o, d, weight='length') if o != d else 0
                                    fila.append(dist)
                                except: fila.append(999999)
                            matriz.append(fila)
                        
                        # 3. Algoritmo Genético
                        def calc_fit(ruta):
                            d = matriz[0][ruta[0]]
                            for i in range(len(ruta)-1): d += matriz[ruta[i]][ruta[i+1]]
                            d += matriz[ruta[-1]][0]
                            return d

                        pedidos = list(range(1, len(nodos)))
                        poblacion = [random.sample(pedidos, len(pedidos)) for _ in range(50)]
                        
                        for _ in range(150): # Generaciones
                            poblacion.sort(key=calc_fit)
                            elite = poblacion[:10]
                            nuevos = []
                            while len(nuevos) < 40:
                                p = copy.deepcopy(random.choice(elite))
                                if len(p) > 1:
                                    a, b = random.sample(range(len(p)), 2)
                                    p[a], p[b] = p[b], p[a]
                                nuevos.append(p)
                            poblacion = elite + nuevos
                        
                        mejor_ruta = min(poblacion, key=calc_fit)
                        dist_total = calc_fit(mejor_ruta)

                        # 4. Reconstruir Ruta
                        secuencia = [nodos[0]] + [nodos[i] for i in mejor_ruta] + [nodos[0]]
                        ruta_final = []
                        for k in range(len(secuencia)-1):
                            camino = nx.shortest_path(G, secuencia[k], secuencia[k+1], weight='length')
                            ruta_final.extend(camino[:-1])
                        ruta_final.append(secuencia[-1])
                        
                        coords_ruta = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in ruta_final]
                        st.session_state['ruta_calculada'] = coords_ruta
                        st.balloons() # ¡Efecto de celebración!
                        st.info(f"Distancia Total: {dist_total/1000:.2f} km")
                        st.rerun()