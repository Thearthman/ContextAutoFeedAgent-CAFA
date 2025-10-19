@echo off
chcp 65001 >nul
echo ========================================
echo Memory Tool 对话场景测试
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 检查测试数据...
if not exist chatgpt_export.json (
    echo [警告] 未找到 chatgpt_export.json
    echo [提示] 正在使用示例数据...
    copy chatgpt_export_example.json chatgpt_export.json >nul 2>&1
    if errorlevel 1 (
        echo [错误] 无法创建测试数据
        echo.
        echo 请运行以下命令准备数据:
        echo   python tests\import_chatgpt_history.py
        pause
        exit /b 1
    )
    echo [成功] 已使用示例数据
)

echo [2/3] 检查依赖...
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

echo [3/3] 启动测试...
echo.

REM 运行对话场景测试
python tests\test_memory_with_conversation.py

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 查看结果:
echo   • 测试报告: memory_test_report.json
echo   • 记忆数据: test_conversation_memory.json
echo.
echo 下一步:
echo   • 调整存储策略以优化效果
echo   • 测试不同的衰减参数
echo   • 集成到实际应用中
echo.
pause


