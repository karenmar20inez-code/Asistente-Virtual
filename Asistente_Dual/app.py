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

# --- FUNCIONES DE VOZ Y ASISTENTE ---
def guardar_nombre():
    if st.session_state.widget_nombre:
        st.session_state.nombre_usuario = st.session_state.widget_nombre.title()
        st.session_state.widget_nombre = "" 
        nombre = st.session_state.nombre_usuario
        if "Nexy" in st.session_state.radio_asistente:
            msg = f"¡Obvio te iba a saludar, {nombre}! Bienvenida a la Central Diamond 💅✨. Pídeme lo que quieras."
        else:
            msg = f"Sistemas en línea, {nombre}. Cyberx a tu servicio 🤖🛠️. ¿Qué ejecutamos?"
        st.session_state.mensaje = msg
        st.session_state.hablar_texto = msg

def cambio_asistente():
    nombre = st.session_state.nombre_usuario
    es_nexy_nuevo = "Nexy" in st.session_state.radio_asistente
    if nombre:
        msg = f"Cambio de turno. Ahora estás con {'Nexy Diamond' if es_nexy_nuevo else 'Cyberx'}, {nombre}."
    else:
        msg = "Cambiando interfaz de asistente."
    st.session_state.mensaje = msg
    st.session_state.hablar_texto = msg

# --- 4. BARRA LATERAL ---
st.sidebar.markdown("### ⚙️ Configuración")
if st.session_state.nombre_usuario:
    st.sidebar.success(f"👤 Usuario: **{st.session_state.nombre_usuario}**")
st.sidebar.text_input("Ingresa tu nombre:", key="widget_nombre", on_change=guardar_nombre)
genero = st.sidebar.radio("🤖 Asistente:", ["👨 Cyberx", "💅 Nexy Diamond"], key="radio_asistente", on_change=cambio_asistente)
modo_oscuro = st.sidebar.toggle("🌙 Modo Oscuro", value=True)
es_nexy = "Nexy" in genero

# --- 5. DISEÑO RESPONSIVO ---
color_tema = "#FF007F" if es_nexy else "#00E5FF"
color_resplandor = f"{color_tema}66"
bg_color = "#0a0a0c" if modo_oscuro else "#ffffff"
text_color = "#ffffff" if modo_oscuro else "#1e1e1e"
card_bg = "#16161a" if modo_oscuro else "#f0f0f0"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; }}
    .titulo {{ color: {color_tema}; text-align: center; font-weight: 900; letter-spacing: 4px; margin-bottom: 2rem; text-transform: uppercase; text-shadow: 0px 0px 15px {color_tema}; }}
    .consola {{ padding: 20px; background: {card_bg}; border: 2px solid {color_tema}; border-radius: 12px; color: {text_color}; font-size: 1.1rem; text-align: center; margin-bottom: 2rem; box-shadow: 0 0 15px {color_resplandor}; }}
    div.stButton > button {{ background-color: transparent !important; color: {text_color} !important; border-radius: 10px !important; border: 2px solid {color_tema} !important; font-weight: bold !important; width: 100% !important; }}
    div.stButton > button:hover {{ background-color: {color_tema} !important; color: #000 !important; box-shadow: 0 0 10px {color_tema} !important; }}
    
    @media screen and (max-width: 768px) {{
        div[data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 8px !important; justify-content: center !important; }}
        div[data-testid="column"] {{ flex: 0 0 30% !important; min-width: 30% !important; max-width: 32% !important; padding: 0 !important; }}
        div.stButton > button {{ font-size: 10px !important; height: 40px !important; min-height: 40px !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 class='titulo'>{'✨ NEXY DIAMOND' if es_nexy else '🤖 CYBERX'}</h1>", unsafe_allow_html=True)

# --- 6. PANEL DE CONTROL (CON AUTO-PAUSA) ---
def set_mensaje(msg_cyberx, msg_nexy):
    # Función para pausar música al pedir info
    st.session_state.reproduciendo = False 
    respuesta = msg_nexy if es_nexy else msg_cyberx
    st.session_state.mensaje = respuesta
    st.session_state.hablar_texto = respuesta 

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

if col1.button("⌚ Hora"):
    ahora = datetime.datetime.now(zona_horaria).strftime('%H:%M')
    set_mensaje(f"Tiempo del sistema: {ahora}.", f"Son las {ahora}, gordi. El tiempo vuela.")

if col2.button("📅 Fecha"):
    dia = datetime.date.today()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    set_mensaje(f"Fecha actual: {dia.day} de {meses[dia.month-1]}.", f"Hoy es {dia.day} de {meses[dia.month-1]}, obvio.")

if col3.button("🌤️ Clima"):
    try:
        r = requests.get("https://wttr.in/Mexico+City?format=%t|%C&m&lang=es", timeout=5)
        r.encoding = 'utf-8' 
        t, c = unquote(r.text.strip()).replace('+', '').split('|')
        num = t.replace('°C', '').strip()
        set_mensaje(f"Sensores indican {num} grados centígrados y {c.lower()}.", f"Hace {num} grados centígrados y está {c.lower()} en la ciudad.")
    except:
        set_mensaje("Error en sensores climáticos.", "No tengo el clima ahora, gordi.")

if col4.button("💵 Dólar"):
    try:
        d = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
        set_mensaje(f"Divisa: 1 dólar es igual a {d:.2f} pesos mexicanos.", f"El dólar está en {d:.2f} pesos. ¡Carísimo!")
    except:
        set_mensaje("Error de conexión financiera.", "No sé en cuánto está el dólar hoy.")

if col5.button("😂 Chiste"):
    chiste = pyjokes.get_joke('es')
    set_mensaje(chiste, f"O sea, escucha este chiste: {chiste}")

if col6.button("🗑️ Borrar"):
    set_mensaje("Buffer limpio. Pantalla en blanco.", "Todo limpio y perfecto como yo.")

st.markdown(f"<div class='consola'>{st.session_state.mensaje}</div>", unsafe_allow_html=True)

# --- REPRODUCTOR DE VOZ NATIVO (Diferencia Hombre/Mujer) ---
if st.session_state.hablar_texto:
    texto = st.session_state.hablar_texto.replace('"', '').replace("'", "")
    es_mujer_js = "true" if es_nexy else "false"
    components.html(f"""
    <script>
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{texto}");
        var voices = window.speechSynthesis.getVoices();
        var esMujer = {es_mujer_js};
        var spanV = voices.filter(v => v.lang.startsWith('es'));
        
        // Selección de voz por género
        var vEle = esMujer 
            ? spanV.find(v => v.name.includes('Monica') || v.name.includes('Helena') || v.name.includes('Paulina')) 
            : spanV.find(v => v.name.includes('Raul') || v.name.includes('Jorge') || v.name.includes('Diego'));
        
        if(!vEle && spanV.length > 0) vEle = spanV[0];
        if(vEle) msg.voice = vEle;
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """, height=0)
    st.session_state.hablar_texto = ""

# ==========================================
# --- 7. REPRODUCTOR MUSICAL CON VOZ ---
# ==========================================
st.markdown(f"<h3 style='text-align:center; color:{color_tema};'>📻 Reproductor Musical</h3>", unsafe_allow_html=True)

if st.session_state.playlist.actual:
    st.markdown(f"<div style='text-align:center; padding:15px; border:1px solid {color_tema}; border-radius:10px;'>🎵 <b>SONANDO:</b> {st.session_state.playlist.actual.cancion.nombre}</div>", unsafe_allow_html=True)

col_sh, col_an, col_pl, col_si, col_re = st.columns(5)

# MIX / ALEATORIO
lbl_sh = "🔀 Mix ON" if st.session_state.modo_aleatorio else "🔀 Mix OFF"
if col_sh.button(lbl_sh):
    st.session_state.modo_aleatorio = not st.session_state.modo_aleatorio
    st.session_state.hablar_texto = f"Modo aleatorio {'activado' if st.session_state.modo_aleatorio else 'desactivado'}."
    st.rerun()

# ANTERIOR
if col_an.button("⏮️ Anterior"):
    if st.session_state.modo_aleatorio:
        nodos = []
        t = st.session_state.playlist.cabeza
        while t: nodos.append(t); t = t.siguiente
        st.session_state.playlist.actual = random.choice(nodos)
    elif st.session_state.playlist.actual and st.session_state.playlist.actual.anterior:
        st.session_state.playlist.actual = st.session_state.playlist.actual.anterior
    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Poniendo la canción anterior."
    st.rerun()

# PLAY / PAUSE
lbl_p = "⏸️ Pausar" if st.session_state.reproduciendo else "▶️ Tocar"
if col_pl.button(lbl_p):
    st.session_state.reproduciendo = not st.session_state.reproduciendo
    st.session_state.hablar_texto = "Música pausada." if not st.session_state.reproduciendo else "Reproduciendo música."
    st.rerun()

# SIGUIENTE
if col_si.button("⏭️ Siguiente"):
    if st.session_state.modo_aleatorio:
        nodos = []
        t = st.session_state.playlist.cabeza
        while t: nodos.append(t); t = t.siguiente
        st.session_state.playlist.actual = random.choice(nodos)
    elif st.session_state.playlist.actual and st.session_state.playlist.actual.siguiente:
        st.session_state.playlist.actual = st.session_state.playlist.actual.siguiente
    st.session_state.reproduciendo = True
    st.session_state.hablar_texto = "Siguiente canción en la lista."
    st.rerun()

# BUCLE / REPETIR
lbl_r = "🔁 Bucle ON" if st.session_state.modo_repetir else "🔁 Bucle OFF"
if col_re.button(lbl_r):
    st.session_state.modo_repetir = not st.session_state.modo_repetir
    st.session_state.hablar_texto = f"Repetición {'activada' if st.session_state.modo_repetir else 'desactivada'}."
    st.rerun()

if st.session_state.playlist.actual:
    st.audio(st.session_state.playlist.actual.cancion.ruta, autoplay=st.session_state.reproduciendo, loop=st.session_state.modo_repetir)
