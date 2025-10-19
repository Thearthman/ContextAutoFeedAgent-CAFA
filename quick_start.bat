@echo off
chcp 65001 >nul
title ContextAutoFeedAgent-CAFA 快速启动

echo.
echo ============================================================
echo 🚀 ContextAutoFeedAgent-CAFA 快速启动器
echo ============================================================
echo.

echo 📋 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 🚀 快速启动...
python quick_start.py

echo.
echo 👋 程序结束
pause
