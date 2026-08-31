@echo off
chcp 65001 >nul
title CoomerTool Installer
color 0B
echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                                                               ║
echo  ║           🚀  CoomerTool v1.0.0 Installer                      ║
echo  ║           Fast Kemono ^& Coomer Archive Downloader            ║
echo  ║                                                               ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo  [INFO] Python detected.
python --version
echo.

:: Create project directory
set "INSTALL_DIR=%USERPROFILE%\CoomerTool"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo  [INFO] Installing to: %INSTALL_DIR%
echo.

:: Clone or update repo
echo  [INFO] Downloading CoomerTool from GitHub...
echo.

if exist "%INSTALL_DIR%\.git" (
    git pull origin main
) else (
    git clone https://github.com/GangTailorUpgrade/CoomeRtool.git . 2>nul
    if errorlevel 1 (
        echo  [WARN] Git not found or clone failed. Falling back to curl download...
        echo.
        curl -L -o coomertool.zip https://github.com/GangTailorUpgrade/CoomeRtool/archive/refs/heads/main.zip >nul 2>&1
        if errorlevel 1 (
            echo  [ERROR] Download failed. This usually means:
            echo.
            echo    1. Your internet connection is slow or unstable.
            echo    2. GitHub is being throttled in your region.
            echo    3. A firewall or ISP is blocking the connection.
            echo.
            echo  💡 TRY THESE FIXES:
            echo    • Connect to a VPN and run this installer again.
            echo    • Wait 30 seconds and retry the same command.
            echo    • Use a different network (mobile hotspot, etc.).
            echo    • Download manually from: https://github.com/GangTailorUpgrade/CoomeRtool
            echo.
            pause
            exit /b 1
        )
        tar -xf coomertool.zip --strip-components=1 >nul 2>&1
        del coomertool.zip >nul 2>&1
    )
)

echo  [INFO] Installing Python dependencies...
echo.
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  [ERROR] pip install failed. Common causes:
    echo    • Slow / unstable internet connection.
    echo    • PyPI being blocked or throttled in your region.
    echo.
    echo  💡 TRY THESE FIXES:
    echo    • Run the installer again — it will resume.
    echo    • Use a VPN and retry.
    echo    • Try: pip install -r requirements.txt --timeout 120
    echo.
    pause
    exit /b 1
)

echo.
echo  ╔═══════════════════════════════════════════════════════════════╗
echo  ║                    ✅ INSTALLATION COMPLETE                    ║
echo  ╚═══════════════════════════════════════════════════════════════╝
echo.
echo  📁 Installed to: %INSTALL_DIR%
echo.
echo  🚀 Quick Start Commands:
echo    cd /d "%INSTALL_DIR%"
echo    python -m coomertool --help
echo    python -m coomertool "URL" --all
echo.
echo  📝 Example:
echo    python -m coomertool "https://kemono.su/patreon/user/12345" --all --threads 64
echo.
pause
