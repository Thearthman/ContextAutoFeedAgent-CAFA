@echo off
chcp 65001 >nul
echo ========================================
echo Memory Tool 单元测试
echo ========================================
echo.
echo 这是标准的程序员测试方式
echo 验证每个功能是否正常工作
echo.
echo 测试内容:
echo   • 向量化功能
echo   • 记忆存储
echo   • 搜索功能
echo   • 时间衰减
echo   • 持久化
echo   • 边界情况
echo   • 性能测试
echo.
echo 正在运行测试...
echo.

cd ..
python tests\test_memory_unit.py

echo.
pause


