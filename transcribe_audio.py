import whisper
import os
import sys

def transcribe_audio(audio_path, model_name="base"):
    """
    Transcribe un archivo de audio usando OpenAI Whisper.
    Args:
        audio_path (str): Ruta al archivo de audio.
        model_name (str): Nombre del modelo Whisper a usar (tiny, base, small, medium, large).
    """
    if not os.path.exists(audio_path):
        print(f"❌ Error: El archivo no existe: {audio_path}")
        return

    print(f"🔄 Cargando modelo Whisper '{model_name}'...")
    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"❌ Error cargando el modelo: {e}")
        return

    try:
        # Transcribir el audio
        result = model.transcribe(audio_path, fp16=False)
        
        print("\n✅ Transcripción completada. Generando formato guión...")
        print("=" * 60)

        # Preparar contenido con formato de guión (segmentos)
        script_lines = []
        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            # Formato: [MM:SS] Texto...
            line = f"[{start_time} -> {end_time}] {text}"
            script_lines.append(line)
            
            # Opcional: Imprimir en consola los primeros
            if len(script_lines) < 10: 
                print(line)
        
        if len(script_lines) >= 10:
            print("... (resto del contenido en el archivo) ...")

        print("=" * 60)

        # Guardar en archivo de texto
        output_file = audio_path + "_guion.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"TRANSCRIPCIÓN TIPO GUIÓN - {os.path.basename(audio_path)}\n")
            f.write("="*80 + "\n\n")
            f.write("\n".join(script_lines))
        
        print(f"💾 Guión guardado en: {output_file}")

    except Exception as e:
        print(f"❌ Error durante la transcripción: {e}")

def format_timestamp(seconds):
    """Convierte segundos a formato MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    # Ruta del archivo especificada por el usuario
    audio_file = r"C:\Users\petra\Documents\TraductorX\audioPETRA.aac"
    
    # Puedes cambiar el modelo aquí si deseas mayor precisión (ej. "small", "medium")
    # "base" es un buen equilibrio entre velocidad y precisión.
    transcribe_audio(audio_file, model_name="base")
