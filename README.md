# 🌐 TraductorX - Real-Time Audio Translator
# 🌐 TraductorX - Traductor de Audio en Tiempo Real

---


## Español |

Un traductor de audio en tiempo real que captura el audio del sistema, lo transcribe usando OpenAI Whisper, traduce al español y reproduce la traducción en voz. Perfecto para Twitter Spaces, reuniones o cualquier contenido de audio en vivo.

### Características

- Captura de audio del sistema en tiempo real
- Transcripción con OpenAI Whisper (muy preciso)
- Traducción automática Inglés → Español
- Salida de voz con tecnología neural (Edge-TTS)
- Historial de sesión con marcas de tiempo
- Latencia de ~5 segundos

### Requisitos

- Python 3.8 o superior
- Windows 10/11
- ~1GB de espacio libre (para el modelo Whisper)
- FFmpeg (para procesamiento de audio)
- Conexión a internet (para traducción y TTS)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Luis-Cwk/TraductorX.git
cd TraductorX

# Instalar dependencias
pip install -r requirements.txt
```

O ejecuta `install.bat` en Windows.

### Configuración de VB-Cable (Recomendado)

1. Descarga VB-Cable desde https://vb-audio.com/Cable/
2. Instala como administrador y reinicia tu computadora
3. En Configuración de Sonido de Windows:
   - Establece "CABLE Input" como dispositivo de reproducción predeterminado (temporalmente)
   - Habilita "CABLE Output" en la pestaña Grabar
   - Restaura tus bocinas reales como predeterminado

### Uso

```bash
python translator.py
```

El programa te pedirá seleccionar:
- **Dispositivo de entrada**: CABLE Output (VB-Audio Virtual Cable)
- **Dispositivo de salida**: Tus bocinas/auriculares reales

### Configuración

| Parámetro | Ubicación | Descripción |
|-----------|-----------|-------------|
| Modelo Whisper | `translator.py:42` | `tiny`, `base`, `small`, `medium` |
| Voz | `translator.py:98` | `es-ES-ElviraNeural`, `es-MX-DaliaNeural` |
| Duración del chunk | `translator.py:28` | Segundos antes de procesar |

### Cómo Funciona

```
[Fuente de Audio] → [VB-Cable] → [Whisper] → [Traductor] → [TTS] → [Bocinas]
```

### Solución de Problemas

| Problema | Solución |
|----------|----------|
| No detecta VB-Cable | Reinstala VB-Cable como admin, reinicia PC |
| No hay salida de voz | Selecciona bocinas reales, no VB-Cable |
| Audio mezclado | Configura el navegador para usar solo "CABLE Input" |

### Licencia

Gratuito para uso personal.

---

## English | 

A real-time audio translator that captures system audio, transcribes it using OpenAI Whisper, translates to Spanish, and speaks the translation aloud. Perfect for Twitter Spaces, meetings, or any live audio content.

### Features

- Real-time audio capture from system
- Transcription with OpenAI Whisper (highly accurate)
- Automatic translation English → Spanish
- Text-to-speech output with neural voice (Edge-TTS)
- Session logging with timestamps
- ~5 second latency

### Requirements

- Python 3.8+
- Windows 10/11
- ~1GB free space (for Whisper model)
- FFmpeg (for audio processing)
- Internet connection (for translation and TTS)

### Installation

```bash
# Clone the repository
git clone https://github.com/Luis-Cwk/TraductorX.git
cd TraductorX

# Install dependencies
pip install -r requirements.txt
```

Or run `install.bat` on Windows.

### VB-Cable Setup (Recommended)

1. Download VB-Cable from https://vb-audio.com/Cable/
2. Install as administrator and restart your computer
3. In Windows Sound Settings:
   - Set "CABLE Input" as default playback device (temporarily)
   - Enable "CABLE Output" in Recording tab
   - Restore your real speakers as default

### Usage

```bash
python translator.py
```

The program will prompt you to select:
- **Input device**: CABLE Output (VB-Audio Virtual Cable)
- **Output device**: Your real speakers/headphones

### Configuration

| Parameter | Location | Description |
|-----------|----------|-------------|
| Whisper model | `translator.py:42` | `tiny`, `base`, `small`, `medium` |
| Voice | `translator.py:98` | `es-ES-ElviraNeural`, `es-MX-DaliaNeural` |
| Chunk duration | `translator.py:28` | Seconds before processing |

### How It Works

```
[Audio Source] → [VB-Cable] → [Whisper] → [Translator] → [TTS] → [Speakers]
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No VB-Cable detected | Reinstall VB-Cable as admin, restart PC |
| No voice output | Select real speakers, not VB-Cable |
| Mixed audio | Configure browser to use only "CABLE Input" |

### License

Free for personal use.

---

<a name="español"></a>

Hecho con ❤️ | Made with ❤️  
