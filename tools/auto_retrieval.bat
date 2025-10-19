@echo off
chcp 65001 >nul
echo ========================================
echo Memory Tool 自动检索测试
echo ========================================
echo.
echo 这个工具会:
echo   • 自动加载对话数据
echo   • 批量测试所有记忆的检索效果
echo   • 分析相似度分布
echo   • 生成详细检索报告
echo.
echo 配置:
echo   • 对话数: 5 个
echo   • 每个对话消息数: 20 条
echo   • 检索结果数: 5 条
echo.
echo 正在启动...
echo.

cd ..
python tests\auto_retrieval_test.py --file conversations.json --conversations 5 --messages 20 --top-k 5

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 查看结果:
echo   • auto_retrieval_memory.json - 记忆数据
echo   • auto_retrieval_report.json - 检索报告
echo.
pause


