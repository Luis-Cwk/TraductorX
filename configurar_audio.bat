@echo off
chcp 65001 >nul
echo ============================================
echo   CONFIGURAR AUDIO DEL NAVEGADOR
echo ============================================
echo.
echo Para redirigir el audio del Twitter Space al VB-Cable:
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  OPCION 1: Windows 11 (Configuracion por app)     ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo 1. Abre Configuracion de Windows (Win + I)
echo 2. Ve a: Sistema ^> Sonido ^> Mezclador de volumen
echo 3. Busca tu navegador (Chrome, Edge, Firefox)
echo 4. Cambia el dispositivo de salida a "CABLE Input"
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  OPCION 2: Cambiar dispositivo predeterminado    ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo 1. Click derecho en icono de volumen (barra de tareas)
echo 2. "Configuracion de sonido"
echo 3. En "Salida" selecciona "CABLE Input"
echo 4. ABRE EL NAVEGADOR Y TWITTER SPACE
echo 5. Vuelve a poner tus bocinas como predeterminado
echo 6. El audio ya estara redirigido al VB-Cable
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  OPCION 3: Usar Chrome con flag especial          ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo Crea un acceso directo a Chrome con este destino:
echo.
echo "C:\Program Files\Google\Chrome\Application\chrome.exe" --audio-output-channels=2 --audio-output-device="CABLE Input"
echo.
echo ============================================
pause
