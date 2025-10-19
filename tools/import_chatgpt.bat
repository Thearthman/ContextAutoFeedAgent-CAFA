@echo off
chcp 65001 >nul
echo ========================================
echo ChatGPT 聊天记录导入工具
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [1/3] 检查依赖...
python -c "import sentence_transformers" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少必要的依赖包
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/3] 依赖检查完成
echo [3/3] 启动导入脚本...
echo.

REM 运行导入脚本
python tests\import_chatgpt_history.py

echo.
echo ========================================
echo 导入完成！
echo ========================================
echo.
echo 接下来你可以：
echo   1. 运行基础测试: python tests\test_memory_basic.py
echo   2. 启动 API 服务: python run_memory_api.py
echo   3. 查看文档: docs\CHATGPT_IMPORT_GUIDE.md
echo.
pause


