@echo off
chcp 65001 >nul
title CAFA - ContextAutoFeedAgent 统一启动器

echo.
python start_cafa.py

if errorlevel 1 (
    echo.
    echo [错误] 启动失败
    echo.
    pause
    exit /b 1
)

pause

