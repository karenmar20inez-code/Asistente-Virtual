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
            msg = f"O sea, ¡obvio te iba a saludar, {nombre}! Bienvenida a la Central Diamond 💅✨💎. Pídeme lo que quieras."
        else:
            msg = f"Sistemas en línea, {nombre}. Cyberx a tu servicio 🤖🛠️💻. ¿Qué ejecutamos?"
            
        st.session_state.mensaje = msg
        st.session_state.hablar_texto = msg

def cambio_asistente():
    nombre = st.session_state.nombre_usuario
    es_nexy_nuevo = "Nexy" in st.session_state.radio_asistente
    
    if nombre:
        if es_nexy_nuevo:
            msg = f"Cambio de turno. Ahora estás con Nexy Diamond, {nombre}"
        else:
            msg = f"Cargando interfaz Cyberx, {nombre}. Protocolos listos."
    else:
        if es_nexy_nuevo:
            msg = "O sea, ya llegué. Cero estrés por favor."
        else:
            msg = "Cyberx activo. Esperando identificación de usuario."
            
    st.session_state.mensaje = msg
    st.session_state.hablar_texto = msg

# --- 4. BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.markdown("### ⚙️ Configuración")

if st.session_state.nombre_usuario:
    st.sidebar.success(f"👤 Usuario: **{st.session_state.nombre_usuario}**")

st.sidebar.text_input("Ingresa tu nombre:", key="widget_nombre", on_change=guardar_nombre)

genero = st.sidebar.radio("🤖 Asistente:", ["👨 Cyberx", "💅 Nexy Diamond"], key="radio_asistente", on_change=cambio_asistente)
modo_oscuro = st.sidebar.toggle("🌙 Modo Oscuro", value=True)
es_nexy = "Nexy" in genero

# --- 5. DISEÑO SÚPER LLAMATIVO Y RESPONSIVO UNIVERSAL ---
if es_nexy:
    color_tema = "#FF007F" 
    color_resplandor = "#FF007F66"
else:
    color_tema = "#00E5FF" 
    color_resplandor = "#00E5FF66"

bg_color = "#0a0a0c" if modo_oscuro else "#ffffff"
sidebar_color = "#111114" if modo_oscuro else "#f7f7f8"
text_color = "#ffffff" if modo_oscuro else "#1e1e1e"
card_bg = "#16161a" if modo_oscuro else "#f0f0f0"
btn_hover_text = "#000000" if modo_oscuro else "#ffffff"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_color} !important; border-right: 1px solid {color_tema}33; }}
    .titulo {{ color: {color_tema}; text-align: center; font-weight: 900; letter-spacing: 4px; margin-bottom: 2rem; text-transform: uppercase; text-shadow: 0px 0px 15px {color_tema}; }}
    .consola {{ padding: 25px; background: {card_bg}; border: 2px solid {color_tema}; border-radius: 12px; color: {text_color}; font-size: 1.15rem; text-align: center; margin: 2rem 0; box-shadow: 0 0 20px {color_resplandor}; }}
    
    /* Estilo Base de Botones */
    div.stButton > button {{ background-color: transparent !important; color: {text_color} !important; border-radius: 10px !important; border: 2px solid {color_tema} !important; font-weight: bold !important; width: 100% !important; transition: all 0.3s ease !important; }}
    div.stButton > button:hover {{ background-color: {color_tema} !important; color: {btn_hover_text} !important; box-shadow: 0 0 15px {color_tema} !important; }}
    div.stLinkButton > a {{ background-color: {color_tema} !important; color: {btn_hover_text} !important; border-radius: 10px !important; font-weight: 900 !important; width: 100% !important; display: flex; align-items: center; justify-content: center; text-decoration: none; }}

    /* =========================================================
       REPARACIÓN DE GRID RESPONSIVO (ANDROID & iOS)
       ========================================================= */
    @media screen and (max-width: 768px) {{
        /* Forzamos a que las columnas no se apilen */
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            justify-content: center !important;
        }}
        /* Cada columna ocupa un tercio aproximado */
        div[data-testid="column"] {{
            flex: 0 0 30% !important;
            min-width: 30% !important;
            max-width: 32% !important;
            padding: 0 !important;
        }}
        /* Botones compactos para que quepan 3 */
        div.stButton > button {{
            font-size: 10px !important;
            height: 40px !important;
            min-height: 40px !important;
            padding: 0 !important;
        }}
        /* Ajuste para el buscador (2 columnas en móvil) */
        .buscador-grid div[data-testid="column"] {{
            flex: 0 0 48% !important;
            min-width: 48% !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

nombre_ui = "✨ NEXY DIAMOND" if es_nexy else "🤖 CYBERX"
st.markdown(f"<h1 class='titulo'>{nombre_ui}</h1>", unsafe_allow_html=True)

# --- 6. FUNCIONES DE LÓGICA ---
def set_mensaje(msg_cyberx, msg_nexy):
    respuesta = msg_nexy if es_nexy else msg_cyberx
    st.session_state.mensaje = respuesta
    st.session_state.hablar_texto = respuesta 

# PANEL DE CONTROL (6 BOTONES)
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

if col1.button("⌚ Hora"):
    ahora = datetime.datetime.now(zona_horaria).strftime('%H:%M')
    set_mensaje(f"Tiempo del sistema: {ahora}.", f"Son las {ahora}. Qué rápido pasa el tiempo.")

if col2.button("📅 Fecha"):
    dia = datetime.date.today()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    set_mensaje(f"Fecha actual: {dia.day} de {meses[dia.month-1]}.", f"Es {dia.day} de {meses[dia.month-1]}.")

if col3.button("🌤️ Clima"):
    try:
        r = requests.get("https://wttr.in/Mexico+City?format=%t|%C&m&lang=es", timeout=5)
        r.encoding = 'utf-8' 
        t, c = unquote(r.text.strip()).replace('+', '').split('|')
        numero_grados = t.replace('°C', '').replace('°F', '').replace('°', '').strip()
        set_mensaje(
            f"Sensores indican {numero_grados}°C y {c.lower()}.", 
            f"Hace {numero_grados} grados centígrados y está {c.lower()}, gordi."
        )
    except:
        set_mensaje("Fallo en sensores climáticos.", "No tengo el dato del clima ahorita.")

if col4.button("💵 Dólar"):
    try:
        d = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
        set_mensaje(f"Divisa: 1 USD = {d:.2f} MXN.", f"El dólar está en {d:.2f} pesos.")
    except:
        set_mensaje("Error de conexión financiera.", "El sistema bancario no responde.")

if col5.button("😂 Chiste"):
    set_mensaje(pyjokes.get_joke('es'), f"O sea, escucha esto: {pyjokes.get_joke('es')}")

if col6.button("🗑️ Borrar"):
    set_mensaje("Buffer limpio. Listo.", "Lista y limpia. ¿Qué sigue?")

st.markdown(f"<div class='consola'>{st.session_state.mensaje}</div>", unsafe_allow_html=True)

# --- REPRODUCTOR DE VOZ (JS) ---
if st.session_state.hablar_texto:
    texto_seguro = st.session_state.hablar_texto.replace('"', '').replace("'", "").replace('\n', ' ')
    es_mujer_js = "true" if es_nexy else "false"
    components.html(f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{texto_seguro}");
        var voices = window.speechSynthesis.getVoices();
        var esMujer = {es_mujer_js};
        var spanV = voices.filter(v => v.lang.startsWith('es'));
        var vEle = esMujer ? spanV.find(v => v.name.includes('Monica') || v.name.includes('Helena')) : spanV.find(v => v.name.includes('Raul') || v.name.includes('Jorge'));
        if(vEle) msg.voice = vEle;
        msg.rate = 1.05;
        window.speechSynthesis.speak(msg);
    </script>
    """, height=0)
    st.session_state.hablar_texto = ""

# ==========================================
# --- 7. EXPLORAR ---
# ==========================================
st.markdown("#### 🔍 Explorar")
motor = st.radio("Motor:", ["Google", "YouTube", "Wikipedia"], horizontal=True)

# Contenedor especial para el buscador responsivo
st.markdown('<div class="buscador-grid">', unsafe_allow_html=True)
c_in, c_bt = st.columns(2)
with c_in:
    busqueda = st.text_input("Buscando...", placeholder="Investigar...", label_visibility="collapsed")
with c_bt:
    if busqueda:
        if motor == "Wikipedia":
            if st.button("📖 WIKI", use_container_width=True):
                try:
                    wiki = wikipediaapi.Wikipedia(user_agent="BotDual/1.0", language='es')
                    p = wiki.page(busqueda)
                    if p.exists():
                        set_mensaje(f"Resumen Cyberx: {p.summary[:200]}...", f"Encontré esto: {p.summary[:200]}...")
                    else:
                        set_mensaje("Sin resultados en base de datos.", "Wikipedia no sabe de eso.")
                except: set_mensaje("Error de red.", "Wiki fuera de línea.")
        else:
            url = f"https://www.google.com/search?q={busqueda.replace(' ', '+')}" if motor == "Google" else f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
            st.link_button(f"🚀 {motor.upper()}", url, use_container_width=True)
    else:
        st.button("BUSCAR", disabled=True, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# --- 8. REPRODUCTOR MUSICAL ---
# ==========================================
st.markdown(f"<h3 style='text-align:center; color:{color_tema};'>📻 Reproductor</h3>", unsafe_allow_html=True)

if st.session_state.playlist.actual:
    st.markdown(f"""
        <div style='text-align:center; padding: 15px; border-radius: 12px; background: {card_bg}; border: 1px solid {color_tema};'>
            <div style='font-size: 0.8rem; color:{color_tema};'>🎵 SONANDO</div>
            <div style='font-size: 1.1rem; font-weight: bold;'>{st.session_state.playlist.actual.cancion.nombre}</div>
        </div>
    """, unsafe_allow_html=True)

col_sh, col_an, col_pl, col_si, col_re = st.columns(5)

if col_sh.button("🔀", help="Aleatorio"):
    st.session_state.modo_aleatorio = not st.session_state.modo_aleatorio
    st.rerun()
if col_an.button("⏮️"):
    if st.session_state.playlist.actual:
        if st.session_state.modo_aleatorio:
            # Lógica simple de aleatorio
            pass 
        st.session_state.reproduciendo = True
        st.rerun()
if col_pl.button("⏯️"):
    st.session_state.reproduciendo = not st.session_state.reproduciendo
    st.rerun()
if col_si.button("⏭️"):
    if st.session_state.playlist.actual:
        if st.session_state.playlist.actual.siguiente:
            st.session_state.playlist.actual = st.session_state.playlist.actual.siguiente
        st.session_state.reproduciendo = True
        st.rerun()
if col_re.button("🔁"):
    st.session_state.modo_repetir = not st.session_state.modo_repetir
    st.rerun()

if st.session_state.playlist.actual:
    st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=st.session_state.reproduciendo)
