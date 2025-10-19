@echo off
chcp 65001 >nul
echo ========================================
echo 测试 Conversations.json 文件
echo ========================================
echo.

REM 检查文件是否存在
if not exist conversations.json (
    echo [错误] 找不到 conversations.json 文件
    echo.
    echo 请确保:
    echo   1. 从 ChatGPT 导出了对话数据
    echo   2. 文件命名为 conversations.json
    echo   3. 文件在项目根目录
    echo.
    pause
    exit /b 1
)

echo [✓] 找到 conversations.json
echo.
echo 配置:
echo   • 处理对话数: 3 (可修改)
echo   • 每个对话消息数: 20 (可修改)
echo.
echo 正在启动测试...
echo.

python tests\test_large_conversations.py --file conversations.json --conversations 3 --messages 20

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 结果文件: test_large_conversations_memory.json
echo.
echo 要测试更多对话，运行:
echo   python tests\test_large_conversations.py --conversations 10 --messages 30
echo.
pause

