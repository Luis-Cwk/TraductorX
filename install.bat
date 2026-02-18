@echo off
chcp 65001 >nul
echo ==========================================
echo   INSTALADOR DE TRADUCTOR DE TWITTER
echo ==========================================
echo.

:: Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8+ desde python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

:: Verificar pip
echo 🔍 Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado. Instalando...
    python -m ensurepip --upgrade
)
echo ✅ pip encontrado

:: Instalar dependencias
echo.
echo 📦 Instalando dependencias (esto puede tardar unos minutos)...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo ✅ ¡Dependencias instaladas correctamente!
echo.
echo ==========================================
echo   CONFIGURACIÓN DE VB-CABLE REQUERIDA
echo ==========================================
echo.
echo Para usar el traductor, necesitas instalar VB-Cable:
echo.
echo 1. 🌐 Ve a: https://vb-audio.com/Cable/
echo 2. ⬇️ Descarga "VB-Cable Virtual Audio Device"
echo 3. 📦 Ejecuta VBCABLE_Setup_x64.exe como ADMINISTRADOR
echo 4. 🔄 REINICIA tu computadora
echo.
echo DESPUÉS DE REINICIAR:
echo - Abre Twitter Space en tu navegador
echo - Ejecuta: python translator.py
echo - Selecciona CABLE Output como entrada
echo - Selecciona tus bocinas como salida
echo - ¡Escucha la traducción en español!
echo.
pause

echo.
echo 🚀 Para iniciar el traductor, ejecuta:
echo    python translator.py
echo.
pause
