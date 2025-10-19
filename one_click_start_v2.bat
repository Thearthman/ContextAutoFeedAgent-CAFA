@echo off
chcp 65001 >nul
title ContextAutoFeedAgent-CAFA 一键启动

echo.
echo ============================================================
echo ContextAutoFeedAgent-CAFA 一键启动程序
echo ============================================================
echo.

echo 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装或未添加到PATH
    echo 请先安装Python并添加到系统PATH
    pause
    exit /b 1
)

echo [OK] Python环境正常

echo.
echo 启动程序...
python one_click_start_v2.py

echo.
echo 程序结束
pause
