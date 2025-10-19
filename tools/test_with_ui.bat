@echo off
chcp 65001 >nul
title 悬浮窗口检索测试

echo.
echo ============================================================
echo 🎯 悬浮窗口检索测试
echo ============================================================
echo.
echo 这个脚本会帮你：
echo 1. 导入 ChatGPT 历史记录到记忆系统
echo 2. 启动记忆API服务器
echo 3. 启动悬浮窗口UI
echo 4. 在悬浮窗口中进行检索测试
echo.
echo ============================================================
echo.

:: 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo [OK] Python环境正常
echo.

:: 检查历史记录文件
echo 检查历史记录文件...
if exist conversations.json (
    echo [OK] 找到 conversations.json
    set HISTORY_FILE=conversations.json
) else if exist chatgpt_export.json (
    echo [OK] 找到 chatgpt_export.json
    set HISTORY_FILE=chatgpt_export.json
) else if exist chatgpt_export_example.json (
    echo [OK] 找到 chatgpt_export_example.json
    set HISTORY_FILE=chatgpt_export_example.json
) else (
    echo [WARNING] 未找到历史记录文件
    echo.
    echo 请将ChatGPT导出的JSON文件放到项目根目录，命名为:
    echo   - conversations.json (推荐)
    echo   - chatgpt_export.json
    echo.
    pause
    exit /b 1
)
echo.

:: 步骤1: 导入历史记录
echo ============================================================
echo 步骤 1/3: 导入历史记录到记忆系统
echo ============================================================
echo.
echo 导入文件: %HISTORY_FILE%
echo.

python tests/import_chatgpt_history.py %HISTORY_FILE%

if errorlevel 1 (
    echo [ERROR] 导入失败
    pause
    exit /b 1
)

echo.
echo [OK] 导入完成！
echo.
timeout /t 2 >nul

:: 步骤2: 启动记忆API服务器
echo ============================================================
echo 步骤 2/3: 启动记忆API服务器
echo ============================================================
echo.

start "记忆API服务器" cmd /k "python run_memory_api.py"
echo [OK] 记忆服务器已在后台启动
echo.

:: 等待服务器启动
echo 等待服务器启动...
timeout /t 3 >nul

:: 步骤3: 启动悬浮窗口
echo ============================================================
echo 步骤 3/3: 启动悬浮窗口UI
echo ============================================================
echo.
echo 提示: 在悬浮窗口中使用记忆管理功能
echo   1. 点击"记忆管理"按钮
echo   2. 切换到"检索记忆"标签
echo   3. 输入查询关键词进行检索测试
echo.
echo 推荐测试查询:
echo   - Python编程
echo   - 机器学习
echo   - 项目管理
echo   - 或者从导入的对话中选择关键词
echo.
timeout /t 2 >nul

python src/advanced_floating_ui.py

echo.
echo ============================================================
echo 测试结束
echo ============================================================
pause

