@echo off
chcp 65001 >nul
title CAFA - Advanced Floating UI

echo.
echo ============================================================
echo CAFA - Context Auto Feed Agent
echo 完整增强版UI (API切换 + 记忆管理)
echo ============================================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo [OK] Python环境正常









echo.
echo 启动完整增强版UI...
python src/advanced_floating_ui.py

echo.
echo 程序结束
pause
