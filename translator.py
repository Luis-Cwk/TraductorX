#!/usr/bin/env python3
"""
Traductor de Audio en Tiempo Real - REPRODUCCIÓN SECUENCIAL SIN CORTES
=======================================================================
SOLUCIÓN: Las traducciones se reproducen UNA POR UNA, sin solaparse
"""

import numpy as np
import sounddevice as sd
import whisper
from deep_translator import GoogleTranslator
import queue
import threading
import sys
import os
import pyttsx3
import time
from difflib import SequenceMatcher
import wave
import tempfile
import asyncio
import edge_tts
import subprocess
from datetime import datetime

# Configuración
SAMPLE_RATE = 16000
CHUNK_DURATION = 5          # Máximo tiempo antes de forzar corte (aumentado para permitir frases largas)
CHUNK_SAMPLES = SAMPLE_RATE * CHUNK_DURATION
SILENCE_THRESHOLD = 0.01    # Umbral de amplitud para considerar "silencio"
SILENCE_TRIGGER_MS = 600    # Cuántos ms de silencio activan el corte inmediato
MIN_AUDIO_MS = 500          # Mínimo de audio necesario para intentar procesar

ENABLE_VOICE = True
VOICE_SPEED = 200
VOICE_VOLUME = 1.0

class AudioTranslator:
    def __init__(self):
        print("🔄 Cargando modelo Whisper...")
        # fp16=False para compatibilidad asegurada, pero si tienes GPU potente Whisper usará CUDA internamente si está disponible
        self.model = whisper.load_model("tiny")
        self.translator = GoogleTranslator(source='en', target='es')
        self.audio_queue = queue.Queue()
        self.is_running = True
        self.last_text = ""
        
        # Sistema de TTS SECUENCIAL
        self.tts_text_queue = queue.Queue()  # Cola de TEXTOS a convertir
        self.tts_audio_segments = queue.Queue()  # Cola de AUDIOS completos
        
        # Buffer de reproducción actual
        self.playback_lock = threading.Lock()
        self.current_segment = None
        self.current_position = 0
        
        if ENABLE_VOICE:
            # Worker que convierte texto → audio
            self.tts_generator_thread = threading.Thread(target=self._tts_generator_worker, daemon=True)
            self.tts_generator_thread.start()
        
        # Configuración de LOG (Historial)
        self.log_dir = "transcriptions"
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = os.path.join(self.log_dir, f"session_{timestamp}.md")
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"# 📝 Historial de Traducción - {timestamp}\n\n")
            f.write("| Hora | Origen (EN) | Traducción (ES) |\n")
            f.write("|------|-------------|-----------------|\n")
            
        print(f"📂 Guardando historial en: {self.log_file}")
        print("✅ Modelo cargado")
        print("=" * 70)
        
    def save_log(self, text_en, text_es):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Escapar pipes | para evitar romper la tabla markdown
            clean_en = text_en.replace("|", "\|").replace("\n", " ")
            clean_es = text_es.replace("|", "\|").replace("\n", " ")
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"| {timestamp} | {clean_en} | {clean_es} |\n")
        except Exception as e:
            print(f"❌ Error guardando log: {e}")
        
    def speak(self, text):
        if not ENABLE_VOICE or not text:
            return
        self.tts_text_queue.put(text)
    
    def _tts_generator_worker(self):
        """Worker que convierte TEXTO a AUDIO usando Edge-TTS (Neural)"""
        # Voz sugerida: es-ES-ElviraNeural (España, Mujer) o es-MX-DaliaNeural (México, Mujer)
        # Puedes cambiarla aquí.
        VOICE = "es-ES-ElviraNeural"  
        
        print(f"   🗣️  TTS Neural Activo: {VOICE}")
        
        while self.is_running:
            try:
                # Esperar por texto a convertir
                try:
                    text = self.tts_text_queue.get(timeout=1)
                except queue.Empty:
                    continue

                mp3_filename = tempfile.mktemp(suffix=".mp3")
                wav_filename = tempfile.mktemp(suffix=".wav")
                
                try:
                    # 1. Generar Audio MP3 con Edge-TTS (Async)
                    # Ejecutamos la corrutina de forma síncrona en este hilo
                    asyncio.run(self._generate_edge_tts(text, VOICE, mp3_filename))
                    
                    # 2. Convertir a WAV compatible (16kHz, Mono) con FFmpeg
                    # Esto asegura que numpy pueda leerlo sin problemas
                    subprocess.run([
                        "ffmpeg", "-y", "-i", mp3_filename,
                        "-ar", str(SAMPLE_RATE),  # 16000
                        "-ac", "1",               # Mono
                        "-f", "wav", 
                        wav_filename
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    if os.path.exists(wav_filename) and os.path.getsize(wav_filename) > 0:
                        with wave.open(wav_filename, 'rb') as wf:
                            channels = wf.getnchannels()
                            rate = wf.getframerate()
                            frames = wf.readframes(wf.getnframes())
                            
                            dtype = np.int16
                            if wf.getsampwidth() == 1:
                                dtype = np.int8
                            
                            audio_int = np.frombuffer(frames, dtype=dtype)
                            audio_float = audio_int.astype(np.float32) / 32768.0
                            
                            if channels > 1:
                                audio_float = audio_float.reshape(-1, channels).mean(axis=1)

                            # No debería ser necesario resamplear si ffmpeg lo hizo, pero por seguridad:
                            if rate != SAMPLE_RATE:
                                audio_float = self._resample_audio(audio_float, rate, SAMPLE_RATE)
                            
                            duration = len(audio_float) / SAMPLE_RATE
                            
                            self.tts_audio_segments.put({
                                'audio': audio_float,
                                'duration': duration,
                                'text': text[:50] + '...' if len(text) > 50 else text
                            })
                            
                            print(f"   🔊 TTS Neural: {duration:.1f}s | Cola: {self.tts_audio_segments.qsize()}")
                            
                except Exception as e:
                    print(f"❌ Error TTS generación: {e}")
                finally:
                    # Limpieza
                    if os.path.exists(mp3_filename):
                        try: os.remove(mp3_filename)
                        except: pass
                    if os.path.exists(wav_filename):
                        try: os.remove(wav_filename)
                        except: pass
                            
            except Exception as e:
                print(f"❌ Error TTS worker: {e}")

    async def _generate_edge_tts(self, text, voice, filename):
        """Generador async wrapper para edge-tts"""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)
                
    def _resample_audio(self, audio_data, original_rate, target_rate):
        if original_rate == target_rate:
            return audio_data
        duration = len(audio_data) / original_rate
        time_old = np.linspace(0, duration, len(audio_data))
        new_length = int(duration * target_rate)
        time_new = np.linspace(0, duration, new_length)
        return np.interp(time_new, time_old, audio_data)
    
    def is_similar(self, text1, text2, threshold=0.7):
        if not text1 or not text2:
            return False
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > threshold
        
    def select_devices(self):
        """Seleccionar dispositivos"""
        devices = sd.query_devices()
        
        print("\n" + "=" * 70)
        print("   CONFIGURACIÓN DE DISPOSITIVOS")
        print("=" * 70)
        
        print("\n📱 ENTRADA (VB-Cable Output):")
        print("-" * 70)
        
        input_devices = []
        vb_cable_candidates = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
                name_lower = device['name'].lower()
                if 'cable output' in name_lower and 'vb-audio' in name_lower and 'point' not in name_lower:
                    vb_cable_candidates.append((i, device))
                    print(f"[{i}] {device['name']} ⭐")
        
        print("\n🔊 SALIDA (Bocinas físicas):")
        print("-" * 70)
        
        output_devices = []
        speaker_candidates = []
        
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                output_devices.append((i, device))
                name_lower = device['name'].lower()
                
                if 'cable' in name_lower or 'vb-audio' in name_lower or 'virtual' in name_lower:
                    continue
                
                if any(word in name_lower for word in ['speaker', 'altavoc', 'realtek', 'display']):
                    speaker_candidates.append((i, device))
                    if 'realtek' in name_lower:
                        print(f"[{i}] {device['name']} ⭐")
                    else:
                        print(f"[{i}] {device['name']}")
        
        print("\n" + "=" * 70)
        print("💡 ENTRADA: CABLE Output | SALIDA: Speakers/Realtek")
        print("=" * 70)
        print()
        
        if vb_cable_candidates:
            vb_idx = vb_cable_candidates[0][0]
            print(f"✅ VB-Cable: [{vb_idx}]")
            use_auto = input("¿Usar? (Enter=sí): ").strip()
            input_device = vb_idx if use_auto == '' else int(use_auto)
        else:
            input_device = int(input("Dispositivo ENTRADA: "))
        
        print("\n🎯 SALIDA:")
        if speaker_candidates:
            for idx, (dev_idx, dev) in enumerate(speaker_candidates[:3]):
                print(f"   [{dev_idx}] {dev['name']}")
        
        while True:
            output_device = int(input("\nDispositivo SALIDA: "))
            output_name = sd.query_devices(output_device)['name'].lower()
            
            if 'cable' in output_name or 'vb-audio' in output_name:
                print("❌ ERROR: Cable virtual, selecciona bocinas físicas")
                continue
            
            print(f"✅ {sd.query_devices(output_device)['name']}")
            confirm = input("¿Correcto? (Enter=sí): ").strip()
            if confirm == '':
                break
        
        return input_device, output_device
        
    def output_callback(self, outdata, frames, time_info, status):
        """
        Callback de SALIDA - REPRODUCCIÓN SECUENCIAL
        Reproduce un segmento completo antes de pasar al siguiente
        """
        if status:
            print(f"⚠️ {status}")
        
        try:
            with self.playback_lock:
                # Si no hay segmento actual, intentar obtener el siguiente
                if self.current_segment is None:
                    try:
                        segment = self.tts_audio_segments.get_nowait()
                        self.current_segment = segment['audio']
                        self.current_position = 0
                        print(f"\n   ▶️  Reproduciendo: {segment['text']}")
                    except queue.Empty:
                        # No hay nada que reproducir
                        outdata.fill(0)
                        return
                
                # Calcular cuánto audio tenemos disponible
                available = len(self.current_segment) - self.current_position
                
                if available > 0:
                    # Leer lo que necesitamos
                    to_read = min(frames, available)
                    audio_chunk = self.current_segment[
                        self.current_position:self.current_position + to_read
                    ]
                    self.current_position += to_read
                    
                    # Si terminamos este segmento, marcarlo como None para cargar el siguiente
                    if self.current_position >= len(self.current_segment):
                        remaining_queue = self.tts_audio_segments.qsize()
                        print(f"   ✅ Terminado | {remaining_queue} en cola")
                        self.current_segment = None
                        self.current_position = 0
                    
                    # Preparar salida
                    output_buffer = np.zeros(frames, dtype=np.float32)
                    output_buffer[:to_read] = audio_chunk
                    
                    # Convertir a stereo si es necesario
                    if outdata.shape[1] > 1:
                        output_stereo = np.tile(output_buffer.reshape(-1, 1), (1, outdata.shape[1]))
                        outdata[:] = output_stereo
                    else:
                        outdata[:] = output_buffer.reshape(-1, 1)
                else:
                    outdata.fill(0)
                    
        except Exception as e:
            print(f"❌ Error output: {e}")
            import traceback
            traceback.print_exc()
            outdata.fill(0)
    
    def input_callback(self, indata, frames, time_info, status):
        """Callback de ENTRADA"""
        if status:
            print(f"⚠️ Input: {status}")
        
        try:
            if indata.shape[1] > 1:
                mono_input = np.mean(indata, axis=1, keepdims=True)
            else:
                mono_input = indata
            
            self.audio_queue.put(mono_input.copy())
            
        except Exception as e:
            print(f"❌ Error input: {e}")
        
    def process_audio(self):
        """
        Procesa audio con DETECCIÓN DE SILENCIO (VAD simulado)
        Corta y traduce en cuanto detecta una pausa, para mayor fluidez.
        """
        audio_buffer = []
        silence_counter = 0  # Contador de chunks de silencio consecutivos
        
        # Cuántos chunks de silencio equivalen al tiempo de disparo
        # Asumiendo que el callback nos da chunks de ~50ms (blocksize 0.05s)
        blocks_per_second = 20 # 1 / 0.05
        silence_blocks_trigger = int((SILENCE_TRIGGER_MS / 1000.0) * blocks_per_second)
        min_audio_lenght_samples = int((MIN_AUDIO_MS / 1000.0) * SAMPLE_RATE)

        print(f"🔧 Config VAD: Silencio Trigger = {SILENCE_TRIGGER_MS}ms ({silence_blocks_trigger} bloques)")
        
        while self.is_running:
            try:
                chunk = self.audio_queue.get(timeout=1)
                
                # Calcular volumen RMS del chunk actual
                rms = np.sqrt(np.mean(chunk**2))
                
                if rms < SILENCE_THRESHOLD:
                    silence_counter += 1
                else:
                    silence_counter = 0 # Reiniciar si hay ruido/voz
                
                audio_buffer.append(chunk.flatten())
                
                # Calcular longitud actual del buffer
                current_samples = sum(len(a) for a in audio_buffer)
                
                should_process = False
                
                # 1. Criterio de Silencio: Si hemos hablado suficiente Y hay silencio ahora
                if current_samples > min_audio_lenght_samples and silence_counter >= silence_blocks_trigger:
                    should_process = True
                    # print("   ✂️  Corte por silencio")
                
                # 2. Criterio de Tamaño Máximo: Si el buffer se llenó demasiado (evitar overflow)
                elif current_samples >= CHUNK_SAMPLES:
                    should_process = True
                    # print("   ✂️  Corte por tamaño máximo")
                
                if should_process:
                    audio_data = np.concatenate(audio_buffer)
                    audio_buffer = [] # Limpiar buffer
                    silence_counter = 0
                    
                    audio_float = audio_data.astype(np.float32)
                    self.transcribe_and_translate(audio_float)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error proceso: {e}") 
                                
    def transcribe_and_translate(self, audio):
        """Transcribe y traduce"""
        try:
            result = self.model.transcribe(audio, language='en', fp16=False)
            text_en = result["text"].strip()
            
            if text_en and len(text_en) > 3:
                if self.is_similar(text_en, self.last_text):
                    return
                
                self.last_text = text_en
                text_es = self.translator.translate(text_en)
                
                print(f"\n🇺🇸 EN: {text_en}")
                print(f"🇪🇸 ES: {text_es}")
                print("-" * 70)
                
                self.save_log(text_en, text_es)
                self.speak(text_es)
                
        except Exception as e:
            print(f"❌ Error transcripción: {e}")
            
    def run(self):
        """Inicia el sistema"""
        input_device, output_device = self.select_devices()
        
        if input_device is None or output_device is None:
            print("❌ No configurado")
            return
        
        print(f"\n🎙️  ENTRADA: {sd.query_devices(input_device)['name']}")
        print(f"🔊 SALIDA: {sd.query_devices(output_device)['name']}")
        print("\n" + "=" * 70)
        print("📋 MODO: REPRODUCCIÓN SECUENCIAL")
        print("   • Cada traducción se reproduce COMPLETA")
        print("   • Las siguientes esperan en cola")
        print("   • Sin solapamientos ni cortes")
        print("=" * 70)
        print("\n⏳ Iniciando en 3 segundos...")
        
        time.sleep(3)
        
        process_thread = threading.Thread(target=self.process_audio, daemon=True)
        process_thread.start()
        
        try:
            input_stream = sd.InputStream(
                device=input_device,
                channels=1,
                samplerate=SAMPLE_RATE,
                dtype=np.float32,
                blocksize=int(SAMPLE_RATE * 0.05),
                callback=self.input_callback,
            )
            
            output_stream = sd.OutputStream(
                device=output_device,
                channels=2,
                samplerate=SAMPLE_RATE,
                dtype=np.float32,
                blocksize=int(SAMPLE_RATE * 0.05),
                callback=self.output_callback,
            )
            
            print("🟢 ACTIVO")
            print("   (Ctrl+C para detener)\n")
            
            with input_stream, output_stream:
                while self.is_running:
                    sd.sleep(100)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Deteniendo...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            process_thread.join()
            print("✅ Detenido")

def check_requirements():
    try:
        import whisper
        import sounddevice
        import deep_translator
        import numpy
        # import pyttsx3 # Ya no es crítico
        import edge_tts
        return True
    except ImportError as e:
        print("❌ Faltan:", e)
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("   🌐 TRADUCTOR - REPRODUCCIÓN SECUENCIAL")
    print("=" * 70)
    print()
    
    if not check_requirements():
        sys.exit(1)
    
    translator = AudioTranslator()
    translator.run()