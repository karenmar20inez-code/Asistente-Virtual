# 🤖 Central de Mando: Asistente Dual (Nexy Diamond & Elpidio)

¡Bienvenido a la **Central de Mando**! Esta es una aplicación web interactiva desarrollada con Python y Streamlit que funciona como un asistente virtual con doble personalidad. 

La aplicación permite al usuario interactuar con dos perfiles distintos, cada uno con su propio diseño, paleta de colores y voz generada dinámicamente:
* 💅 **Nexy Diamond:** Un asistente elegante, moderno y con un toque "fresa" y sofisticado (Estilo Neón Rosa).
* 🤠 **Elpidio:** Un asistente práctico, de campo y directo (Estilo Neón Cyan).

## ✨ Características Principales

* **Interfaz Dinámica (UI/UX):** Tema claro/oscuro personalizable y diseño minimalista tipo "Ghost Buttons" con animaciones CSS y efectos de resplandor neón.
* **Síntesis de Voz Nativa (TTS):** Integración con la API de `speechSynthesis` de JavaScript para respuestas de voz instantáneas, detectando voces femeninas o masculinas según el asistente elegido.
* **Reproductor Musical Integrado:** Sistema de listas ligadas en Python para reproducir música local, con controles de reproducción (Anterior, Pausa/Play, Siguiente) y modos Aleatorio/Repetir.
* **Consultas en Tiempo Real:** * 🌤️ Clima actual (vía `wttr.in`).
    * 💵 Tipo de cambio del Dólar (vía `yfinance`).
    * 😂 Chistes aleatorios (vía `pyjokes`).
    * 📅 Fecha y ⌚ Hora del sistema.
* **Buscador Inteligente:** Permite hacer consultas rápidas que leen resúmenes de Wikipedia en voz alta, o redirigen con botones de acción seguros hacia Google y YouTube.
* **Saludo Personalizado:** Memoria de sesión que recuerda tu nombre y te saluda de acuerdo a la personalidad del asistente activo.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3
* **Framework Frontend:** Streamlit
* **Integración Web:** HTML, CSS y JavaScript nativo (Streamlit Components)
* **Librerías principales:** `yfinance`, `wikipedia-api`, `pyjokes`, `requests`, `pytz`

## 🚀 Cómo ejecutar el proyecto localmente

1. Clona este repositorio en tu computadora.
2. Instala las dependencias necesarias ejecutando en tu terminal:
   ```bash
   pip install -r requirements.txt