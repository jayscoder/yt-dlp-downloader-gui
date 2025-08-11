@echo off
echo Building Windows executable...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller --clean --noconfirm video_downloader_windows.spec

echo.
echo Build complete! Check the dist folder for the executable.
pause