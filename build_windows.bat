@echo off
echo Building Windows executable...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Activate venv
call venv\Scripts\activate.bat

REM Build the executable (windowed, no console)
pyinstaller --clean --noconfirm video_downloader.spec

echo.
echo Build complete! Check the dist folder for the executable.
pause