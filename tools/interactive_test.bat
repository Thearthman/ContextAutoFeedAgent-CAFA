@echo off
chcp 65001 >nul
echo ========================================
echo Memory Tool 交互式测试工具
echo ========================================
echo.
echo 这个工具允许你:
echo   • 手动输入查询检索记忆
echo   • 手动添加和编辑记忆
echo   • 调整记忆权重
echo   • 查看统计信息
echo   • 从 conversations.json 导入
echo.
echo 正在启动...
echo.

cd ..
python tests\interactive_memory_test.py

pause


