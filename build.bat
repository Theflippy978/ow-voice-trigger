@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   守望先锋语音触发器 - 打包脚本
echo ========================================
echo.
echo [1/3] 安装依赖...
pip install PySide6 pygame-ce pynput psutil pyinstaller Pillow pefile
if errorlevel 1 goto :error
echo.
echo [2/3] 打包中...
pyinstaller --clean ow.spec
if errorlevel 1 goto :error
echo.
echo [3/3] 修复图标资源...
python fix_icon.py
if errorlevel 1 goto :error
echo.
echo [清理缓存]
if exist build rd /s /q build
if exist __pycache__ rd /s /q __pycache__
if exist core\__pycache__ rd /s /q core\__pycache__
if exist ui\__pycache__ rd /s /q ui\__pycache__
echo   缓存清理完成
echo.
echo ========================================
echo   打包完成！
echo   输出文件: dist\OW语音触发器.exe
echo ========================================
pause
goto :eof

:error
echo.
echo ========================================
echo   打包出错！请检查上方错误信息
echo ========================================
pause
exit /b 1
