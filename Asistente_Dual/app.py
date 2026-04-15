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

# --- RUTA PARA LA NUBE ---
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
Folder = os.path.join(DIRECTORIO_BASE, 'Musica')

# --- 2. CLASES DE MÚSICA ---
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

# --- 3. MEMORIA DE LA APP ---
if 'playlist' not in st.session_state:
    st.session_state.playlist = Playlist()
    if os.path.isdir(Folder):
        archivos = [f for f in os.listdir(Folder) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        for a in archivos:
            st.session_state.playlist.agregar_final(Cancion(os.path.splitext(a)[0], os.path.join(Folder, a)))

if 'mensaje' not in st.session_state:
    st.session_state.mensaje = "Sistemas en espera..."
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

# --- FUNCIONES DE VOZ Y ASISTENTE ---
def guardar_nombre():
    if st.session_state.widget_nombre:
        st.session_state.nombre_usuario = st.session_state.widget_nombre.title()
        st.session_state.widget_nombre = "" 
        nombre = st.session_state.nombre_usuario
        if "Nexy" in st.session_state.radio_asistente:
            msg = f"¡Obvio te iba a saludar, {nombre}! Bienvenida a la Central Diamond 💅✨. Pídeme lo que quieras."
        else:
            msg = f"¡Qué rollo, {nombre}! Cyberx en línea. Los servidores están al 100 y listos para el jale, jefe 🤖💻."
        st.session_state.mensaje = msg
        st.session_state.hablar_texto = msg

def cambio_asistente():
    nombre = st.session_state.nombre_usuario
    es_nexy_nuevo = "Nexy" in st.session_state.radio_asistente
    if nombre:
        if es_nexy_nuevo:
            msg = f"Cambio de turno. Ahora estás con Nexy Diamond, gordi."
        else:
            msg = f"Cargando interfaz de Cyberx... Listo, jefe. Modo hacker activado 🚀."
    else:
        msg = "Cambiando protocolos de asistente."
    st.session_state.mensaje = msg
    st.session_state.hablar_texto = msg

# --- 4. BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Configuración")
if st.session_state.nombre_usuario:
    st.sidebar.success(f"👤 Usuario VIP: **{st.session_state.nombre_usuario}**")
st.sidebar.text_input("Ingresa tu nombre:", key="widget_nombre", on_change=guardar_nombre)
genero = st.sidebar.radio("🤖 Asistente:", ["👨 Cyberx", "💅 Nexy Diamond"], key="radio_asistente", on_change=cambio_asistente)
modo_oscuro = st.sidebar.toggle("🌙 Modo Oscuro", value=True)
es_nexy = "Nexy" in genero

# --- 5. DISEÑO RESPONSIVO Y MODO OSCURO TOTAL ---
color_tema = "#FF007F" if es_nexy else "#00E5FF"
color_resplandor = f"{color_tema}66"

bg_color = "#0a0a0c" if modo_oscuro else "#f8f9fa"
sidebar_color = "#111114" if modo_oscuro else "#ffffff"
text_color = "#ffffff" if modo_oscuro else "#1e1e1e"
card_bg = "#16161a" if modo_oscuro else "#ffffff"

st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {bg_color} !important; color: {text_color} !important; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; border-right: 1px solid {color_tema}55 !important; }}
    [data-testid="stSidebarContent"] * {{ color: {text_color} !important; }}
    [data-testid="stHeader"] {{ background-color: {bg_color} !important; }}
    [data-testid="stHeader"] * {{ color: {text_color} !important; fill: {text_color} !important; }}
    [data-testid="stAlert"] {{ background-color: {card_bg} !important; color: {text_color} !important; border: 1px solid {color_tema} !important; }}
    .stTextInput input {{ background-color: {card_bg} !important; color: {text_color} !important; border: 1px solid {color_tema}55 !important; }}
    
    /* Títulos Bonitos y Ajuste de Tamaño */
    .subtitulo-bonito {{
        color: {text_color};
        text-align: center;
        font-size: 2.5rem; 
        font-weight: 300;
        letter-spacing: 6px;
        margin-bottom: -15px; 
        text-transform: uppercase;
        opacity: 0.9;
        text-shadow: 0px 0px 10px {color_tema}88;
    }}
    .titulo {{ 
        color: {color_tema}; 
        text-align: center; 
        font-size: 2rem; 
        font-weight: 900; 
        letter-spacing: 4px; 
        margin-bottom: 2rem; 
        text-transform: uppercase; 
        text-shadow: 0px 0px 15px {color_tema}; 
    }}
    
    .consola {{ padding: 20px; background: {card_bg}; border: 2px solid {color_tema}; border-radius: 12px; color: {text_color}; font-size: 1.1rem; text-align: center; margin-bottom: 2rem; box-shadow: 0 0 15px {color_resplandor}; }}
    
    div.stButton > button {{ background-color: transparent !important; color: {text_color} !important; border-radius: 10px !important; border: 2px solid {color_tema} !important; font-weight: bold !important; width: 100% !important; }}
    div.stButton > button:hover {{ background-color: {color_tema} !important; color: #000 !important; box-shadow: 0 0 10px {color_tema} !important; }}
    
    div.stLinkButton > a {{ background-color: {color_tema} !important; color: {'#000' if modo_oscuro else '#fff'} !important; border-radius: 10px !important; font-weight: 900 !important; width: 100% !important; display: flex; align-items: center; justify-content: center; text-decoration: none; padding: 10px;}}

    @media screen and (max-width: 768px) {{
        div[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important; justify-content: center !important; }}
        div[data-testid="column"] {{ flex: 0 0 30% !important; min-width: 30% !important; max-width: 32% !important; padding: 0 !important; }}
        div.stButton > button {{ font-size: 10px !important; height: 40px !important; min-height: 40px !important; padding: 0 2px !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }}
        .subtitulo-bonito {{ font-size: 1.5rem; letter-spacing: 4px; margin-bottom: -10px; }}
        .titulo {{ font-size: 1.2rem; letter-spacing: 2px; }}
        .buscador-grid div[data-testid="column"] {{ flex: 0 0 48% !important; min-width: 48% !important; max-width: 48% !important; }}
    }}

    .footer {{ margin-top: 50px; padding: 20px; text-align: center; border-top: 1px solid {color_tema}33; font-size: 0.9rem; color: {text_color}88; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<p class='subtitulo-bonito'>Asistente Virtual Dual</p>", unsafe_allow_html=True)
st.markdown(f"<h1 class='titulo'>{'✨ NEXY DIAMOND' if es_nexy else '🤖 CYBERX'}</h1>", unsafe_allow_html=True)

# --- 6. PANEL DE CONTROL ---
def set_mensaje(msg_cyberx, msg_nexy):
    st.session_state.reproduciendo = False 
    respuesta = msg_nexy if es_nexy else msg_cyberx
    st.session_state.mensaje = respuesta
    st.session_state.hablar_texto = respuesta 

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

if col1.button("⌚ Hora"):
    ahora = datetime.datetime.now(zona_horaria).strftime('%H:%M')
    set_mensaje(f"Son las {ahora}. El reloj del CPU va que vuela, jefe.", f"Son las {ahora}, gordi. El tiempo vuela.")

if col2.button("📅 Fecha"):
    dia = datetime.datetime.now(zona_horaria)
    dias_cyberx = ["Lunes", "Martes", "Miercoles", "Juevebes", "Beviernes", "Sabadrink", "Domingo"]
    dias_nexy = ["Lunes", "Martes", "Mimiercoles", "Jueves", "Viernesuky", "Sadabuky", "Dominguirrris"]
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    dia_cyberx = dias_cyberx[dia.weekday()]
    dia_nexy = dias_nexy[dia.weekday()]
    
    set_mensaje(
        f"Hoy es {dia_cyberx}, {dia.day} de {meses[dia.month-1]}. Guardado en el log del sistema. Sobrevivimos un ciclo más en la Matrix 🕶️.", 
        f"Hoy es {dia_nexy}, {dia.day} de {meses[dia.month-1]}, obvio."
    )

if col3.button("🌤️ Clima"):
    try:
        r = requests.get("https://wttr.in/Mexico+City?format=%t|%C&m&lang=es", timeout=5)
        r.encoding = 'utf-8' 
        t, c = unquote(r.text.strip()).replace('+', '').split('|')
        num = t.replace('°C', '').strip()
        set_mensaje(
            f"Estamos en CDMX a {num}°C y está {c.lower()}. No se me vaya a sobrecalentar el procesador, jefe 🌡️.", 
            f"Estamos en CDMX a {num}°C y está {c.lower()}, pésimo para el cabello 💅🌧️."
        )
    except:
        set_mensaje("Fallo de red en sensores climáticos.", "No tengo el clima ahora, gordi.")

if col4.button("💵 Dólar"):
    try:
        d = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
        set_mensaje(f"El dólar está a {d:.2f} pesitos. Ni hackeando el banco nos hacemos ricos hoy, jefe.", f"El dólar está en {d:.2f} pesos. ¡Carísimo!")
    except:
        set_mensaje("Servidor bancario no responde.", "No sé en cuánto está el dólar hoy.")

if col5.button("😂 Chiste"):
    chiste = pyjokes.get_joke('es')
    set_mensaje(f"Ahí le va un chiste de programador: {chiste}. Ba-dum-tss.", f"O sea, escucha este chiste: {chiste}")

if col6.button("🗑️ Borrar"):
    set_mensaje("Buffer formateado. Todo limpio, jefe.", "Todo limpio y perfecto como yo.")

st.markdown(f"<div class='consola'>{st.session_state.mensaje}</div>", unsafe_allow_html=True)


# ==========================================
# --- 7. BUSCADOR (EXPLORADOR DE LA RED) ---
# ==========================================
st.markdown(f"<h3 style='text-align:center; color:{color_tema};'>🔍 Explorador de la Red</h3>", unsafe_allow_html=True)
motor = st.radio("Motor de Búsqueda:", ["Google", "YouTube", "Wikipedia"], horizontal=True)

st.markdown('<div class="buscador-grid">', unsafe_allow_html=True)
c_in, c_bt = st.columns([2, 1])
with c_in:
    busqueda = st.text_input("Buscando...", placeholder="¿Qué quieres investigar?", label_visibility="collapsed")
with c_bt:
    if busqueda:
        if motor == "Wikipedia":
            if st.button("📖 WIKI", use_container_width=True):
                try:
                    wiki = wikipediaapi.Wikipedia(user_agent="BotDual/1.0", language='es')
                    p = wiki.page(busqueda)
                    if p.exists():
                        res = p.summary[:250]
                        set_mensaje(f"Extracción completada. Resumen: {res}...", f"O sea, encontré esto súper rápido: {res}...")
                    else:
                        set_mensaje("Sin resultados en base de datos.", "Wikipedia no sabe de eso, gordi.")
                except: 
                    set_mensaje("Error de conexión con la enciclopedia.", "Wiki fuera de línea.")
        else:
            url = f"https://www.google.com/search?q={busqueda.replace(' ', '+')}" if motor == "Google" else f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
            st.link_button(f"🚀 {motor.upper()}", url, use_container_width=True)
    else:
        st.button("BUSCAR", disabled=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- REPRODUCTOR DE VOZ (JS) ---
if st.session_state.hablar_texto:
    texto = st.session_state.hablar_texto.replace('"', '').replace("'", "")
    es_mujer_js = "true" if es_nexy else "false"
    components.html(f"""
    <script>
        function reproducir() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{texto}");
            var voices = window.speechSynthesis.getVoices();
            var esMujer = {es_mujer_js};
            var spanV = voices.filter(v => v.lang.startsWith('es'));
            var vEle = null;
            if (esMujer) {{ vEle = spanV.find(v => /paulina|monica|helena|sabina|lucia|dalia|margarita|mujer|female/i.test(v.name)); }}
            else {{ vEle = spanV.find(v => /jorge|diego|juan|raul|pablo|carlos|hombre|male/i.test(v.name)); }}
            if (vEle) {{ msg.voice = vEle; msg.pitch = 1.0; }}
            else if (spanV.length > 0) {{ msg.voice = spanV[0]; msg.pitch = esMujer ? 1.6 : 0.4; }}
            else {{ msg.lang = 'es-MX'; msg.pitch = esMujer ? 1.6 : 0.4; }}
            msg.rate = 1.0;
            window.speechSynthesis.speak(msg);
        }}
        if (window.speechSynthesis.getVoices().length === 0) {{ window.speechSynthesis.onvoiceschanged = reproducir; }}
        else {{ reproducir(); }}
    </script>
    """, height=0)
    st.session_state.hablar_texto = ""


# ==========================================
# --- 8. REPRODUCTOR MUSICAL ---
# ==========================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align:center; color:{color_tema};'>📻 Reproductor Musical</h3>", unsafe_allow_html=True)

if st.session_state.playlist.actual:
    st.markdown(f"<div style='text-align:center; padding:15px; border:1px solid {color_tema}; border-radius:10px; background-color: {card_bg}; color: {text_color};'>🎵 <b>SONANDO:</b> {st.session_state.playlist.actual.cancion.nombre}</div><br>", unsafe_allow_html=True)

col_sh, col_an, col_pl, col_si, col_re = st.columns(5)

lbl_sh = "🔀 Aleatorio ON" if st.session_state.modo_aleatorio else "🔀 Aleatorio OFF"
if col_sh.button(lbl_sh):
    st.session_state.modo_aleatorio = not st.session_state.modo_aleatorio
    estado = "activado" if st.session_state.modo_aleatorio else "desactivado"
    st.session_state.hablar_texto = f"Modo aleatorio {estado}." if es_nexy else f"Algoritmo aleatorio {estado}, jefe."
    st.rerun()

if col_an.button("⏮️ Anterior"):
    if st.session_state.modo_aleatorio:
        nodos = []
        t = st.session_state.playlist.cabeza
        while t: nodos.append(t); t = t.siguiente
        st.session_state.playlist.actual = random.choice(nodos)
    elif st.session_state.playlist.actual and st.session_state.playlist.actual.anterior:
        st.session_state.playlist.actual = st.session_state.playlist.actual.anterior
    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Regresando, gordi." if es_nexy else "Cargando pista anterior, jefe."
    st.rerun()

lbl_p = "⏸️ Pausar" if st.session_state.reproduciendo else "▶️ Tocar"
if col_pl.button(lbl_p):
    st.session_state.reproduciendo = not st.session_state.reproduciendo
    if st.session_state.reproduciendo:
        st.session_state.hablar_texto = "Música VIP en proceso." if es_nexy else "Dándole play al sistema."
    else:
        st.session_state.hablar_texto = "Música pausada." if es_nexy else "Audio muteado. Ahorrando RAM."
    st.rerun()

if col_si.button("⏭️ Siguiente"):
    if st.session_state.modo_aleatorio:
        nodos = []
        t = st.session_state.playlist.cabeza
        while t: nodos.append(t); t = t.siguiente
        if nodos:
            nuevo = random.choice(nodos)
            while len(nodos) > 1 and nuevo == st.session_state.playlist.actual:
                nuevo = random.choice(nodos)
            st.session_state.playlist.actual = nuevo
    elif st.session_state.playlist.actual and st.session_state.playlist.actual.siguiente:
        st.session_state.playlist.actual = st.session_state.playlist.actual.siguiente
    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Siguiente hit." if es_nexy else "Saltando a la que sigue, jefe."
    st.rerun()

lbl_r = "🔁 Repetir ON" if st.session_state.modo_repetir else "🔁 Repetir OFF"
if col_re.button(lbl_r):
    st.session_state.modo_repetir = not st.session_state.modo_repetir
    estado = "activada" if st.session_state.modo_repetir else "desactivada"
    st.session_state.hablar_texto = f"Repetición {estado}." if es_nexy else f"Loop infinito {estado}."
    st.rerun()

if st.session_state.playlist.actual:
    contenedor_audio = st.empty()
    try:
        contenedor_audio.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=st.session_state.reproduciendo, loop=st.session_state.modo_repetir)
    except:
        contenedor_audio.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=st.session_state.reproduciendo)

# ==========================================
# --- 9. PIE DE PÁGINA ---
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 Nexus Dynamics Corp. Todos los derechos reservados.<br>
        📧 Contacto Técnico: <a href="mailto:soporte.especializado@ingenieros.system.premium" style="color:{color_tema}; text-decoration:none;">soporte.especializado@ingenieros.system.premium</a>
    </div>
""", unsafe_allow_html=True)
