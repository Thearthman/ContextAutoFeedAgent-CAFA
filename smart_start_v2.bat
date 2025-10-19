@echo off
chcp 65001 >nul
title ContextAutoFeedAgent-CAFA 智能启动器

echo.
echo ============================================================
echo 🚀 ContextAutoFeedAgent-CAFA 智能启动器
echo ============================================================
echo.

echo 📋 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 💡 请先安装Python并添加到系统PATH
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🚀 启动智能启动器...
python smart_launcher_v2.py

echo.
echo 👋 程序结束
pause
