@echo off
echo =====================================
echo   智能视频下载工具 Windows 版打包
echo =====================================
echo.
echo Building Windows executable...

REM 检查logo文件
if not exist logo.png (
    echo 错误: logo.png 文件不存在！
    echo 请确保 logo.png 文件在当前目录中
    pause
    exit /b 1
)
echo 找到 logo.png 文件

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Activate venv
call venv\Scripts\activate.bat

REM Build the executable (windowed, no console)
echo 正在使用 logo.png 作为应用图标...
pyinstaller --clean --noconfirm video_downloader.spec

echo.
if exist "dist\智能视频下载工具" (
    echo =====================================
    echo 打包成功！
    echo 应用程序位置: dist\智能视频下载工具
    echo 应用图标: logo.png 已成功集成
    echo =====================================
) else (
    echo 打包失败！请检查错误信息
)
pause