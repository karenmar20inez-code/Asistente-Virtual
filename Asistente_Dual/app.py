import os
import datetime
import pytz
import requests
from urllib.parse import unquote
import yfinance as yf
import pyjokes
import wikipediaapi
import streamlit as st
import streamlit.components.v1 as components
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Central de Mando", page_icon="🤖", layout="centered")

zona_horaria = pytz.timezone('America/Mexico_City')
# --- RUTA INTELIGENTE PARA LA NUBE ---
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
Folder = os.path.join(DIRECTORIO_BASE, 'Musica')

# --- 2. CLASES DE MÚSICA (Listas Ligadas) ---
class Cancion:
    def __init__(self, nombre, ruta):
        self.nombre = nombre
        self.ruta = ruta

class Nodo:
    def __init__(self, cancion):
        self.cancion = cancion
        self.anterior = None
        self.siguiente = None

class Playlist:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.actual = None
        
    def agregar_final(self, cancion):
        nuevo = Nodo(cancion)
        if self.cabeza is None: 
            self.cabeza = nuevo
            self.cola = nuevo
        else: 
            nuevo.anterior = self.cola
            self.cola.siguiente = nuevo
            self.cola = nuevo
        if self.actual is None: 
            self.actual = self.cabeza

# --- 3. MEMORIA DE LA APP (Session State) ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = Playlist()
    if os.path.isdir(Folder):
        archivos = [f for f in os.listdir(Folder) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        for a in archivos:
            st.session_state.playlist.agregar_final(Cancion(os.path.splitext(a)[0], os.path.join(Folder, a)))

if 'mensaje' not in st.session_state:
    st.session_state.mensaje = "Esperando órdenes..."
if 'link_busqueda' not in st.session_state:
    st.session_state.link_busqueda = ""
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'hablar_texto' not in st.session_state:
    st.session_state.hablar_texto = "" 
if 'nombre_usuario' not in st.session_state:
    st.session_state.nombre_usuario = ""
if 'reproduciendo' not in st.session_state:
    st.session_state.reproduciendo = False
if 'modo_aleatorio' not in st.session_state:
    st.session_state.modo_aleatorio = False
if 'modo_repetir' not in st.session_state:
    st.session_state.modo_repetir = False

# --- FUNCIONES DE BIENVENIDA Y CAMBIO DE ASISTENTE ---
def guardar_nombre():
    if st.session_state.widget_nombre:
        st.session_state.nombre_usuario = st.session_state.widget_nombre.title()
        st.session_state.widget_nombre = "" 
        
        nombre = st.session_state.nombre_usuario
        if "Nexy" in st.session_state.radio_asistente:
            msg = f"O sea, ¡obvio te iba a saludar, {nombre}! Bienvenida a la Central Diamond. Pídeme lo que quieras."
        else:
            msg = f"¡Qué rollo, {nombre}! Bienvenido a la Central de Mando de Elpidio. A la orden, patrón."
            
        st.session_state.mensaje = msg
        st.session_state.hablar_texto = msg

def cambio_asistente():
    nombre = st.session_state.nombre_usuario
    es_nexy_nuevo = "Nexy" in st.session_state.radio_asistente
    
    if nombre:
        if es_nexy_nuevo:
            msg = f"Cambio de turno. Ahora estás con Nexy Diamond, {nombre}"
        else:
            msg = f"Ya llegó Elpidio al relevo, {nombre}. ¿En qué le damos?"
    else:
        if es_nexy_nuevo:
            msg = "O sea, ya llegué. Cero estrés por favor."
        else:
            msg = "¡Qué onda patrón! Listo para el jale."
            
    st.session_state.mensaje = msg
    st.session_state.hablar_texto = msg
    st.session_state.link_busqueda = ""

# --- 4. BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.markdown("### ⚙️ Configuración")

if st.session_state.nombre_usuario:
    st.sidebar.success(f"👤 Usuario VIP: **{st.session_state.nombre_usuario}**")

st.sidebar.text_input("Ingresa tu nombre y dale Enter:", key="widget_nombre", on_change=guardar_nombre)

genero = st.sidebar.radio("🤖 Asistente:", ["👨 Elpidio", "💅 Nexy Diamond"], key="radio_asistente", on_change=cambio_asistente)
modo_oscuro = st.sidebar.toggle("🌙 Modo Oscuro", value=True)
es_nexy = "Nexy" in genero

# --- 5. DISEÑO SÚPER LLAMATIVO (ESTILO NEÓN) ---
if es_nexy:
    color_tema = "#FF007F" if modo_oscuro else "#D81B60"
    color_resplandor = "#FF007F66"
else:
    color_tema = "#00E5FF" if modo_oscuro else "#00509E"
    color_resplandor = "#00E5FF66"

bg_color = "#0a0a0c" if modo_oscuro else "#ffffff"
sidebar_color = "#111114" if modo_oscuro else "#f7f7f8"
text_color = "#ffffff" if modo_oscuro else "#1e1e1e"
card_bg = "#16161a" if modo_oscuro else "#f0f0f0"
btn_hover_text = "#000000" if modo_oscuro else "#ffffff"

st.markdown(f"""
    <style>
    @keyframes pulse {{
        0% {{ transform: scale(1); box-shadow: 0 0 10px {color_resplandor}; }}
        50% {{ transform: scale(1.02); box-shadow: 0 0 25px {color_tema}; }}
        100% {{ transform: scale(1); box-shadow: 0 0 10px {color_resplandor}; }}
    }}

    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; border-right: 1px solid {color_tema}33; box-shadow: 2px 0 15px {color_resplandor}; }}
    [data-testid="stSidebar"] * {{ color: {text_color} !important; }}

    .titulo {{ color: {color_tema}; text-align: center; font-weight: 900; letter-spacing: 4px; margin-bottom: 2rem; text-transform: uppercase; text-shadow: 0px 0px 15px {color_tema}; }}
    
    .consola {{ padding: 25px; background: {card_bg}; border: 2px solid {color_tema}; border-radius: 12px; color: {text_color}; font-size: 1.15rem; font-weight: 500; text-align: center; margin: 2rem 0; box-shadow: 0 0 20px {color_resplandor}; }}
    
    div.stButton > button {{ background-color: transparent !important; color: {text_color} !important; border-radius: 10px !important; border: 2px solid {color_tema} !important; font-weight: bold !important; width: 100% !important; height: 50px !important; transition: all 0.3s ease !important; box-shadow: 0 0 10px {color_resplandor} !important; }}
    div.stButton > button:hover {{ background-color: {color_tema} !important; color: {btn_hover_text} !important; box-shadow: 0 0 25px {color_tema} !important; transform: translateY(-3px); }}

    div.stLinkButton > a {{ background-color: {color_tema} !important; color: {btn_hover_text} !important; border-radius: 10px !important; font-weight: 900 !important; width: 100% !important; height: 50px !important; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 0 0 15px {color_resplandor} !important; transition: all 0.3s ease !important;}}
    div.stLinkButton > a:hover {{ transform: translateY(-3px); box-shadow: 0 0 25px {color_tema} !important; }}

    .stTextInput input, div[data-baseweb="select"] > div {{ 
        background-color: {card_bg} !important; 
        color: {text_color} !important; 
        -webkit-text-fill-color: {text_color} !important;
        border-radius: 10px !important; 
        border: 1px solid {color_tema}88 !important; 
        padding: 12px 15px !important; 
    }}
    .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within {{ 
        border-color: {color_tema} !important; 
        box-shadow: 0 0 15px {color_resplandor} !important; 
    }}
    
    div[data-baseweb="popover"] div, div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li, div[data-baseweb="popover"] span {{ background-color: {card_bg} !important; color: {text_color} !important; }}
    div[data-baseweb="popover"] li:hover {{ background-color: {color_tema} !important; color: {btn_hover_text} !important; }}
    
    hr {{ border-top: 1px solid {color_tema}55; margin: 2rem 0; }}
    </style>
    """, unsafe_allow_html=True)

nombre_ui = "✨ NEXY DIAMOND" if es_nexy else "🛠️ ELPIDIO"
st.markdown(f"<h1 class='titulo'>{nombre_ui}</h1>", unsafe_allow_html=True)

# --- 6. FUNCIONES DE LÓGICA ---
def set_mensaje(msg_elpidio, msg_nexy):
    respuesta = msg_nexy if es_nexy else msg_elpidio
    st.session_state.mensaje = respuesta
    st.session_state.hablar_texto = respuesta 

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

if col1.button("⌚ Hora"):
    ahora = datetime.datetime.now(zona_horaria).strftime('%H:%M')
    set_mensaje(f"Son las {ahora}. ¡A darle!", f"Son las {ahora}. Qué rápido pasa el tiempo.")

if col2.button("📅 Fecha"):
    dia = datetime.date.today()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    set_mensaje(f"Hoy es {dia.day} de {meses[dia.month-1]}.", f"Es {dia.day} de {meses[dia.month-1]}.")

if col3.button("🌤️ Clima"):
    try:
        # Agregamos '&m' para forzar grados Celsius y '&lang=es' para español
        r = requests.get("https://wttr.in/Mexico+City?format=%t|%C&m&lang=es", timeout=5)
        r.encoding = 'utf-8' 
        
        t, c = unquote(r.text.strip()).replace('+', '').split('|')
        
        # Limpiamos el texto para quedarnos solo con el puro número
        numero_grados = t.replace('°C', '').replace('°F', '').replace('°', '').strip()
        
        # set_mensaje( Mensaje_Escrito, Mensaje_Hablado )
        set_mensaje(
            f"CDMX a {numero_grados}°C y el cielo está {c.lower()}.", 
            f"O sea estamos a {numero_grados} grados centígrados y está {c.lower()} en la ciudad."
        )
    except:
        set_mensaje("Error de clima.", "No tengo el dato del clima ahorita.")
if col4.button("💵 Dólar"):
    try:
        d = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
        set_mensaje(f"El dólar amaneció a {d:.2f} pesos.", f"El dólar está en {d:.2f} pesos.")
    except:
        set_mensaje("Error bancario.", "El sistema financiero no responde.")

if col5.button("😂 Chiste"):
    set_mensaje(pyjokes.get_joke('es'), f"Escucha esto: {pyjokes.get_joke('es')}")

if col6.button("🗑️ Borrar"):
    set_mensaje("Pantalla limpia, patrón.", "Lista y limpia. ¿Qué sigue?")

# Consola de Respuestas Brillante
st.markdown(f"<div class='consola'>{st.session_state.mensaje}</div>", unsafe_allow_html=True)

# --- REPRODUCTOR DE VOZ NATIVO ---
if st.session_state.hablar_texto:
    texto_seguro = st.session_state.hablar_texto.replace('"', '').replace("'", "").replace('\n', ' ')
    es_mujer_js = "true" if es_nexy else "false"
    
    js_code = f"""
    <script>
        function reproducirVoz() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{texto_seguro}");
            var voices = window.speechSynthesis.getVoices();
            var esMujer = {es_mujer_js};
            
            var spanishVoices = voices.filter(function(v) {{ return v.lang.startsWith('es'); }});
            var vozElegida = null;

            if (esMujer) {{
                vozElegida = spanishVoices.find(v => v.name.includes('Sabina') || v.name.includes('Helena') || v.name.includes('Paulina') || v.name.includes('Dalia') || v.name.includes('Monica') || v.name.toLowerCase().includes('female'));
            }} else {{
                vozElegida = spanishVoices.find(v => v.name.includes('Raul') || v.name.includes('Jorge') || v.name.includes('Diego') || v.name.includes('Carlos') || v.name.toLowerCase().includes('male'));
            }}

            if (vozElegida) {{ msg.voice = vozElegida; }} 
            else if (spanishVoices.length > 0) {{ msg.voice = spanishVoices[0]; msg.pitch = esMujer ? 1.2 : 0.8; }} 
            else {{ msg.lang = 'es-MX'; }}
            
            msg.rate = 1.05;
            window.speechSynthesis.speak(msg);
        }}

        if (window.speechSynthesis.getVoices().length === 0) {{
            window.speechSynthesis.onvoiceschanged = reproducirVoz;
        }} else {{ reproducirVoz(); }}
    </script>
    """
    components.html(js_code, height=0, width=0)
    st.session_state.hablar_texto = ""


# ==========================================
# --- 7. BÚSQUEDA A PRUEBA DE FALLOS ---
# ==========================================
st.markdown("#### 🔍 Explorar")

motor = st.radio("Elige el motor de búsqueda:", ["Google", "YouTube", "Wikipedia"], horizontal=True)
col_input, col_boton = st.columns([4, 2])

with col_input:
    busqueda = st.text_input("Investigar...", placeholder="¿Qué quieres buscar?", label_visibility="collapsed")

with col_boton:
    if busqueda:
        if motor == "Wikipedia":
            if st.button("📖 LEER WIKI", use_container_width=True):
                try:
                    wiki = wikipediaapi.Wikipedia(user_agent="BotDual/1.0", language='es')
                    p = wiki.page(busqueda)
                    if p.exists():
                        res_corta = p.summary[:250]
                        set_mensaje(f"La Wiki dice: {res_corta}...", f"Encontré esto, Bestie: {res_corta}...")
                    else:
                        set_mensaje("No hallé nada en la Wiki.", "Wikipedia no tiene información de eso.")
                except: 
                    set_mensaje("Fallo de conexión.", "Wikipedia está fallando ahora mismo.")
        else:
            url = f"https://www.google.com/search?q={busqueda.replace(' ', '+')}" if motor == "Google" else f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
            st.link_button(f"🚀 ABRIR EN {motor.upper()}", url, use_container_width=True)
    else:
        st.button("BUSCAR", disabled=True, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ==========================================
# --- 8. REPRODUCTOR MUSICAL SUPREMO ---
# ==========================================
st.markdown(f"<h3 style='text-align:center; color:{color_tema}; text-shadow: 0 0 10px {color_tema}; margin-bottom: 20px;'>📻 Reproductor Musical</h3>", unsafe_allow_html=True)

if st.session_state.playlist.actual:
    st.markdown(f"""
        <div style='text-align:center; padding: 20px; border-radius: 15px; background: {card_bg}; border: 2px solid {color_tema}; box-shadow: 0 0 25px {color_resplandor}; margin-bottom: 25px;'>
            <div style='font-size: 1rem; color:{color_tema}; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px; font-weight: bold;'>🎵 Sonando Ahora</div>
            <div style='font-size: 1.3rem; font-weight: 800; color:{text_color};'>{st.session_state.playlist.actual.cancion.nombre}</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Sube música a la carpeta './Musica/'")

col_shuf, col_ant, col_play, col_sig, col_rep = st.columns(5)

# --- BOTÓN ALEATORIO ---
lbl_shuf = "🔀 Aleatorio: ON" if st.session_state.modo_aleatorio else "🔀 Aleatorio: OFF"
if col_shuf.button(lbl_shuf, use_container_width=True):
    st.session_state.modo_aleatorio = not st.session_state.modo_aleatorio
    estado = "activado" if st.session_state.modo_aleatorio else "desactivado"
    st.session_state.hablar_texto = f"Modo aleatorio {estado}." if es_nexy else f"Aleatorio {estado}, patrón."
    st.rerun() # <- ESTO FUERZA LA ACTUALIZACIÓN VISUAL INMEDIATA

# --- BOTÓN ANTERIOR ---
if col_ant.button("⏮️ Anterior", use_container_width=True):
    if st.session_state.modo_aleatorio:
        nodos = []
        temp = st.session_state.playlist.cabeza
        while temp:
            nodos.append(temp)
            temp = temp.siguiente
        if nodos:
            st.session_state.playlist.actual = random.choice(nodos)
    else:
        if st.session_state.playlist.actual and st.session_state.playlist.actual.anterior:
            st.session_state.playlist.actual = st.session_state.playlist.actual.anterior
        elif st.session_state.playlist.actual and st.session_state.modo_repetir:
            st.session_state.playlist.actual = st.session_state.playlist.cola

    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Regresando la canción, gordi." if es_nexy else "Va pa'trás la rola, patrón."
    st.rerun() # <- ESTO FUERZA LA ACTUALIZACIÓN VISUAL INMEDIATA

# --- BOTÓN PLAY/PAUSA ---
if col_play.button("⏯️ Pausa/Play", use_container_width=True):
    st.session_state.reproduciendo = not st.session_state.reproduciendo
    if st.session_state.reproduciendo:
        st.session_state.hablar_texto = "Reproduciendo música VIP." if es_nexy else "A darle a la música, mai."
    else:
        st.session_state.hablar_texto = "Música pausada." if es_nexy else "Silencio en la cabina."
    st.rerun() # <- ESTO FUERZA LA ACTUALIZACIÓN VISUAL INMEDIATA

# --- BOTÓN SIGUIENTE ---
if col_sig.button("⏭️ Siguiente", use_container_width=True):
    if st.session_state.modo_aleatorio:
        nodos = []
        temp = st.session_state.playlist.cabeza
        while temp:
            nodos.append(temp)
            temp = temp.siguiente
        if nodos:
            nuevo = random.choice(nodos)
            while len(nodos) > 1 and nuevo == st.session_state.playlist.actual:
                nuevo = random.choice(nodos)
            st.session_state.playlist.actual = nuevo
    else:
        if st.session_state.playlist.actual and st.session_state.playlist.actual.siguiente:
            st.session_state.playlist.actual = st.session_state.playlist.actual.siguiente
        elif st.session_state.playlist.actual and st.session_state.modo_repetir:
            st.session_state.playlist.actual = st.session_state.playlist.cabeza

    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Siguiente hit, obvio." if es_nexy else "La que sigue, primo."
    st.rerun() # <- ESTO FUERZA LA ACTUALIZACIÓN VISUAL INMEDIATA

# --- BOTÓN REPETIR ---
lbl_rep = "🔁 Repetir: ON" if st.session_state.modo_repetir else "🔁 Repetir: OFF"
if col_rep.button(lbl_rep, use_container_width=True):
    st.session_state.modo_repetir = not st.session_state.modo_repetir
    estado = "activada" if st.session_state.modo_repetir else "desactivada"
    st.session_state.hablar_texto = f"Repetición {estado}." if es_nexy else f"Bucle {estado}, listo."
    st.rerun() # <- ESTO FUERZA LA ACTUALIZACIÓN VISUAL INMEDIATA

# --- REPRODUCTOR DE AUDIO FINAL ---
if st.session_state.playlist.actual:
    if st.session_state.reproduciendo:
        try:
            st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=True, loop=st.session_state.modo_repetir)
        except:
            st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=True)
    else:
        try:
            st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=False, loop=st.session_state.modo_repetir)
        except:
            st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=False)
