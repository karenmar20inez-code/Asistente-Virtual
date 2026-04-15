# 🚀 Asistente Virtual: Central de Mando (Nexy & Cyberx)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Build](https://img.shields.io/badge/Estado-Producci%C3%B3n-success.svg)

Una aplicación web interactiva desarrollada en **Python** utilizando el framework **Streamlit**. Este sistema funciona como un panel de control personal y asistente virtual dual, optimizado con diseño responsivo avanzado (Mobile-First) para funcionar perfectamente en dispositivos iOS y Android.

Desarrollado y mantenido bajo la licencia de **Nexus Dynamics Corp.**

## ✨ Características Principales

* **🤖 Asistente Dual (Personalidad Múltiple):** Interfaz intercambiable entre "Nexy Diamond" (estilo informal/sassy) y "Cyberx" (estilo tecnológico/hacker).
* **🗣️ Síntesis de Voz Nativa (TTS):** Integración con la API `SpeechSynthesis` de JavaScript para respuestas de voz automáticas, con algoritmos de reconocimiento de género y ajuste dinámico de tono (Pitch) dependiendo del asistente seleccionado.
* **📱 Diseño Responsivo Nivel Hardware:** CSS inyectado para forzar un Grid perfecto de 3x2 en dispositivos móviles, anulando los bloqueos de diseño nativos de motores como WebKit (Safari/iOS).
* **📻 Reproductor Musical Inteligente:** * Construido utilizando una estructura de datos de **Listas Doblemente Ligadas** (`Clase Nodo` y `Clase Playlist`).
  * Soporte para modos "Aleatorio" (Mix) y "Bucle" (Loop).
  * Auto-pausa inteligente al interactuar con otras funciones del sistema.
  * Solución de asincronía en la nube mediante `st.empty()` para evitar superposición de canales de audio.
* **🛠️ Herramientas Integradas:**
  * **Clima:** Conexión a la API de `wttr.in` para datos en tiempo real.
  * **Finanzas:** Web scraping y consumo de la API de Yahoo Finance (`yfinance`) para el tipo de cambio USD/MXN.
  * **Búsqueda Avanzada:** Motor de consulta directo a la API de `wikipedia-api` y redirección a Google/YouTube.
  * **Utilidades:** Reloj con zona horaria estricta (`pytz`), calendario con arrays personalizados de días, y generador de chistes para programadores (`pyjokes`).

## 📁 Estructura del Proyecto

Para que el sistema funcione correctamente, se requiere la siguiente estructura de carpetas:

```text
Asistente-Virtual/
│
├── Asistente_Dual/
│   ├── app.py              # Código fuente principal de la Central de Mando
│   └── Musica/             # ⚠️ Carpeta OBLIGATORIA para los archivos de audio
│       ├── cancion1.mp3
│       └── cancion2.wav
│
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Este archivo
