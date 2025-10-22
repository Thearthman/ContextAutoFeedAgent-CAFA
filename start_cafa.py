#!/usr/bin/env python3
"""
CAFA 统一启动器 - ContextAutoFeedAgent-CAFA
整合系统启动和测试功能的统一入口
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional

# Windows UTF-8编码支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class CAFALauncher:
    """CAFA统一启动器"""
    
    def __init__(self):
        # Get project root (where this script is located)
        self.project_root = Path(__file__).resolve().parent
        
        # Verify project root
        if not (self.project_root / "tests").exists():
            print(f"[警告] 项目路径可能不正确: {self.project_root}")
            print(f"[警告] tests 目录不存在")
        
        self.services = {
            "memory_api": {
                "name": "记忆API服务器",
                "script": "run_memory_api.py",
                "port": 8000,
                "health_url": "http://localhost:8000/docs",
                "description": "语义记忆存储和检索服务"
            },
            "floating_ui": {
                "name": "悬浮窗口UI",
                "script": "src/advanced_floating_ui.py",
                "port": None,
                "health_url": None,
                "description": "图形化聊天界面"
            },
            "online_api": {
                "name": "在线API服务器",
                "script": "src/online_model_server.py",
                "port": 5001,
                "health_url": "http://localhost:5001/health",
                "description": "使用OpenAI等在线API"
            },
            "local_model": {
                "name": "本地模型服务器",
                "script": "src/model_server.py",
                "port": 5000,
                "health_url": "http://localhost:5000/health",
                "description": "运行本地Gemma模型"
            }
        }
        
        self.processes = {}
        
    def print_banner(self):
        """打印欢迎信息"""
        print("=" * 70)
        print("   _____ _____   ______   _      ____  _   _ _   _  _____ _    _ ______ _____  ")
        print("  / ____|  __ \\ |  ____| | |    / __ \\| \\ | | \\ | |/ ____| |  | |  ____|  __ \\ ")
        print(" | |    | |__) || |__    | |   | |  | |  \\| |  \\| | |    | |__| | |__  | |__) |")
        print(" | |    |  ___/ |  __|   | |   | |  | | . ` | . ` | |    |  __  |  __| |  _  / ")
        print(" | |____| |     | |      | |___| |__| | |\\  | |\\  | |____| |  | | |____| | \\ \\ ")
        print("  \\_____|_|     |_|      |______\\____/|_| \\_|_| \\_|\\_____|_|  |_|______|_|  \\_\\")
        print()
        print("              ContextAutoFeedAgent - 智能上下文自动馈送代理")
        print("=" * 70)
        print()
        
    def show_mode_menu(self):
        """显示模式选择菜单"""
        print()
        print("=" * 70)
        print("🎯 选择模式")
        print("=" * 70)
        print()
        print("  1. 🚀 启动系统 - 日常使用CAFA")
        print("     启动各种服务，进行聊天对话")
        print()
        print("  2. 🧪 运行测试 - 测试Memory Tool")
        print("     测试记忆功能，验证效果")
        print()
        print("  0. 退出")
        print()
        print("=" * 70)
        print()
        
    def get_mode_choice(self) -> str:
        """获取模式选择"""
        while True:
            try:
                choice = input("请选择模式 (0-2): ").strip()
                
                if choice in ['0', '1', '2']:
                    return choice
                else:
                    print("[错误] 无效选择，请输入 0-2")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n用户取消")
                return '0'
    
    # ==================== 系统启动功能 ====================
    
    def check_service_status(self, service_name: str) -> bool:
        """检查服务状态"""
        service = self.services[service_name]
        
        if service["health_url"] is None:
            return False
            
        try:
            response = requests.get(service["health_url"], timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def detect_services(self) -> Dict[str, bool]:
        """检测所有服务状态"""
        print("🔍 检测服务状态...")
        print()
        
        status = {}
        
        for service_name, service_info in self.services.items():
            if service_info["health_url"] is None:
                status[service_name] = False
                print(f"   [-] {service_info['name']}: 需要启动")
                continue
                
            is_running = self.check_service_status(service_name)
            status[service_name] = is_running
            
            if is_running:
                print(f"   [✓] {service_info['name']}: 已运行 (端口 {service_info['port']})")
            else:
                print(f"   [-] {service_info['name']}: 未运行")
        
        print()
        return status
    
    def check_api_config(self) -> bool:
        """检查API配置"""
        print("🔑 检查API配置...")
        
        # 检查环境变量
        env_keys = ["OPENAI_API_KEY", "LLM_API_KEY", "API_KEY"]
        for key in env_keys:
            if os.getenv(key):
                print(f"   [✓] 找到环境变量: {key}")
                return True
        
        # 检查配置文件
        if os.path.exists("api_config.json"):
            try:
                with open("api_config.json", 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get("api_key"):
                        print(f"   [✓] 找到配置文件: api_config.json")
                        return True
            except:
                pass
        
        print(f"   [-] 未找到API配置（在线API服务器将无法使用）")
        return False
    
    def show_startup_menu(self, service_status: Dict[str, bool], has_api_config: bool):
        """显示系统启动菜单"""
        print()
        print("=" * 70)
        print("🚀 系统启动选项")
        print("=" * 70)
        print()
        print("【推荐】快速启动")
        print("  1. 启动悬浮窗口（含记忆功能）⭐⭐⭐⭐")
        print("     - 记忆API服务器 + 悬浮窗口UI")
        print("     - 适合：日常使用、聊天对话")
        print()
        print("【完整功能】")
        print("  2. 启动完整系统（含在线API）")
        print("     - 记忆API + 在线API服务器 + 悬浮窗口")
        print("     - 适合：需要在线AI模型的场景")
        print()
        print("  3. 启动完整系统（含本地模型）")
        print("     - 记忆API + 本地模型服务器 + 悬浮窗口")
        print("     - 适合：有GPU、想用本地模型")
        print()
        print("【单独服务】")
        print("  4. 仅启动记忆API服务器")
        print("  5. 仅启动悬浮窗口UI")
        print("  6. 仅启动在线API服务器")
        print("  7. 仅启动本地模型服务器")
        print()
        print("【其他】")
        print("  8. 自定义选择服务")
        print("  0. 返回主菜单")
        print()
        print("=" * 70)
        print()
        
    def get_startup_choice(self) -> str:
        """获取启动选择"""
        while True:
            try:
                choice = input("请选择 (0-8): ").strip()
                
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                else:
                    print("[错误] 无效选择，请输入 0-8")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n用户取消")
                return '0'
    
    def start_service(self, service_name: str, background: bool = True) -> bool:
        """启动服务"""
        service = self.services[service_name]
        
        if not os.path.exists(service["script"]):
            print(f"[错误] 脚本文件不存在: {service['script']}")
            return False
        
        try:
            print(f"🚀 启动 {service['name']}...")
            
            if background:
                # 后台运行
                if sys.platform == 'win32':
                    # Windows: 使用 start 命令在新窗口运行
                    subprocess.Popen(
                        f'start "CAFA - {service["name"]}" python "{service["script"]}"',
                        shell=True
                    )
                else:
                    # Linux/Mac: 后台运行
                    process = subprocess.Popen(
                        [sys.executable, service["script"]],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.processes[service_name] = process
            else:
                # 前台运行
                process = subprocess.Popen([sys.executable, service["script"]])
                self.processes[service_name] = process
            
            # 等待服务启动
            if service["health_url"]:
                print(f"   等待服务启动...")
                time.sleep(3)  # 给服务一些启动时间
                
                for i in range(10):
                    if self.check_service_status(service_name):
                        print(f"   [✓] {service['name']} 启动成功")
                        return True
                    time.sleep(1)
                
                print(f"   [警告] {service['name']} 可能未成功启动，请检查")
                return True  # 仍然返回True，让用户自己判断
            else:
                print(f"   [✓] {service['name']} 已启动")
                return True
            
        except Exception as e:
            print(f"[错误] 启动 {service['name']} 失败: {e}")
            return False
    
    def custom_selection(self) -> List[str]:
        """自定义选择服务"""
        print()
        print("=" * 50)
        print("自定义服务选择")
        print("=" * 50)
        print()
        
        service_list = list(self.services.keys())
        
        for i, service_name in enumerate(service_list, 1):
            service_info = self.services[service_name]
            print(f"  {i}. {service_info['name']}")
            print(f"     {service_info['description']}")
            print()
        
        print("=" * 50)
        
        while True:
            try:
                choice = input("请选择要启动的服务 (输入数字，多个用逗号分隔，如: 1,2,4): ").strip()
                
                if not choice:
                    continue
                
                # 解析选择
                selections = [s.strip() for s in choice.split(",")]
                selected_services = []
                
                valid = True
                for sel in selections:
                    try:
                        idx = int(sel) - 1
                        if 0 <= idx < len(service_list):
                            selected_services.append(service_list[idx])
                        else:
                            print(f"[错误] 无效选择: {sel}")
                            valid = False
                            break
                    except ValueError:
                        print(f"[错误] 无效输入: {sel}")
                        valid = False
                        break
                
                if valid:
                    return selected_services
                    
            except (KeyboardInterrupt, EOFError):
                print("\n用户取消")
                return []
    
    def start_services(self, service_names: List[str]):
        """启动多个服务"""
        print()
        print("=" * 70)
        print(f"📦 启动选定的服务...")
        print("=" * 70)
        print()
        
        success_count = 0
        
        # UI最后启动
        ui_service = None
        if "floating_ui" in service_names:
            ui_service = "floating_ui"
            service_names = [s for s in service_names if s != "floating_ui"]
        
        # 启动其他服务
        for service_name in service_names:
            is_running = self.check_service_status(service_name)
            
            if is_running:
                print(f"[✓] {self.services[service_name]['name']} 已在运行，跳过")
                success_count += 1
            else:
                if self.start_service(service_name, background=True):
                    success_count += 1
                    time.sleep(2)  # 服务间间隔
        
        # 最后启动UI
        if ui_service:
            print()
            if self.start_service(ui_service, background=False):
                success_count += 1
        
        print()
        print("=" * 70)
        print(f"✅ 启动完成: {success_count}/{len(service_names) + (1 if ui_service else 0)} 个服务")
        print("=" * 70)
        print()
        
        if success_count > 0:
            print("📌 使用提示:")
            print("   • 记忆API文档: http://localhost:8000/docs")
            print("   • 在悬浮窗口中点击'切换API'可选择不同的AI服务")
            print("   • 点击'记忆管理'可进行记忆检索测试")
            print("   • 按 Ctrl+C 可停止程序")
            print()
    
    def run_startup_mode(self):
        """运行系统启动模式"""
        # 检测服务状态
        service_status = self.detect_services()
        
        # 检查API配置
        has_api_config = self.check_api_config()
        
        # 显示菜单
        self.show_startup_menu(service_status, has_api_config)
        
        # 获取用户选择
        choice = self.get_startup_choice()
        
        if choice == '0':
            return  # 返回主菜单
        elif choice == '1':
            # 启动悬浮窗口（含记忆功能）
            self.start_services(["memory_api", "floating_ui"])
        elif choice == '2':
            # 启动完整系统（含在线API）
            if not has_api_config:
                print("[警告] 未检测到API配置，在线API服务器可能无法正常工作")
                confirm = input("是否继续? (y/n): ").strip().lower()
                if confirm != 'y':
                    return
            self.start_services(["memory_api", "online_api", "floating_ui"])
        elif choice == '3':
            # 启动完整系统（含本地模型）
            print("[提示] 本地模型需要GPU支持，首次启动需要下载模型（约15GB）")
            confirm = input("是否继续? (y/n): ").strip().lower()
            if confirm != 'y':
                return
            self.start_services(["memory_api", "local_model", "floating_ui"])
        elif choice == '4':
            # 仅启动记忆API
            self.start_services(["memory_api"])
        elif choice == '5':
            # 仅启动悬浮窗口
            self.start_services(["floating_ui"])
        elif choice == '6':
            # 仅启动在线API
            if not has_api_config:
                print("[错误] 未检测到API配置，无法启动在线API服务器")
                print("请先配置API Key:")
                print("  1. 设置环境变量: OPENAI_API_KEY")
                print("  2. 或创建 api_config.json 文件")
                return
            self.start_services(["online_api"])
        elif choice == '7':
            # 仅启动本地模型
            print("[提示] 本地模型需要GPU支持，首次启动需要下载模型（约15GB）")
            confirm = input("是否继续? (y/n): ").strip().lower()
            if confirm != 'y':
                return
            self.start_services(["local_model"])
        elif choice == '8':
            # 自定义选择
            selected = self.custom_selection()
            if selected:
                self.start_services(selected)
        
        # 保持运行（如果启动了UI）
        if "floating_ui" in self.processes:
            try:
                self.processes["floating_ui"].wait()
            except KeyboardInterrupt:
                print("\n正在停止...")
    
    # ==================== 测试功能 ====================
    
    def show_test_menu(self):
        """显示测试菜单"""
        print()
        print("=" * 70)
        print("🧪 Memory Tool 测试选项")
        print("=" * 70)
        print()
        print("【推荐测试】")
        print("  1. 悬浮窗口检索测试 ⭐⭐⭐⭐ (最直观)")
        print("     - 自动导入历史记录")
        print("     - 启动记忆服务器")
        print("     - 打开可视化UI进行检索测试")
        print()
        print("  2. 自动检索测试 ⭐⭐⭐ (最全面)")
        print("     - 批量自动检索所有记忆")
        print("     - 相似度分布分析")
        print("     - 生成详细JSON报告")
        print()
        print("  3. 交互式测试 ⭐⭐ (最灵活)")
        print("     - 手动输入查询检索记忆")
        print("     - 调整记忆权重")
        print("     - 添加/删除记忆")
        print("     - 时间衰减测试")
        print()
        print("【开发测试】")
        print("  4. 单元测试")
        print("     - 测试基础功能是否正常")
        print("     - 适合开发调试")
        print()
        print("【数据测试】")
        print("  5. 对话数据测试 (conversations.json)")
        print("     - 测试大规模对话数据")
        print("     - 支持自定义数量")
        print()
        print("  6. 记忆对话测试")
        print("     - 模拟真实对话流程")
        print("     - 评估记忆命中率")
        print()
        print("  7. 导入ChatGPT记录")
        print("     - 快速批量导入")
        print("     - 验证向量化效果")
        print()
        print("【其他】")
        print("  0. 返回主菜单")
        print()
        print("=" * 70)
        print()
        
    def get_test_choice(self) -> str:
        """获取测试选择"""
        while True:
            try:
                choice = input("请选择测试 (0-7): ").strip()
                
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7']:
                    return choice
                else:
                    print("[错误] 无效选择，请输入 0-7")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n用户取消")
                return '0'
    
    def run_script(self, script_path: str, description: str, args: list = None):
        """运行测试脚本"""
        full_path = self.project_root / script_path
        
        if not full_path.exists():
            print(f"[错误] 脚本不存在: {full_path}")
            return False
        
        print()
        print("=" * 70)
        print(f"🚀 {description}")
        print("=" * 70)
        print()
        
        try:
            cmd = [sys.executable, str(full_path)]
            if args:
                cmd.extend(args)
            
            # 运行脚本
            result = subprocess.run(cmd, cwd=str(self.project_root))
            
            print()
            if result.returncode == 0:
                print(f"✅ {description} 完成")
            else:
                print(f"⚠️  {description} 结束 (返回码: {result.returncode})")
            
            return True
            
        except Exception as e:
            print(f"[错误] 运行失败: {e}")
            return False
    
    def test_with_ui(self):
        """悬浮窗口检索测试"""
        print()
        print("=" * 70)
        print("🎯 悬浮窗口检索测试")
        print("=" * 70)
        print()
        print("这个测试会：")
        print("  1. 导入 ChatGPT 历史记录到记忆系统")
        print("  2. 启动记忆API服务器（后台）")
        print("  3. 启动悬浮窗口UI")
        print("  4. 在UI中进行可视化检索测试")
        print()
        
        # 检查历史记录文件
        history_files = ["conversations.json", "chatgpt_export.json", "chatgpt_export_example.json"]
        history_file = None
        
        for f in history_files:
            if (self.project_root / f).exists():
                history_file = f
                print(f"✓ 找到历史记录文件: {f}")
                break
        
        if not history_file:
            print("⚠️  未找到历史记录文件")
            print("  建议将ChatGPT导出的JSON文件放到项目根目录")
            print()
        
        print("按 Enter 继续，Ctrl+C 取消...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n取消")
            return
        
        # 导入历史记录
        print()
        print("📥 步骤 1/3: 导入历史记录...")
        self.run_script("tests/import_chatgpt_history.py", "导入ChatGPT历史记录", 
                       [history_file] if history_file else [])
        
        print()
        print("⏳ 等待2秒...")
        time.sleep(2)
        
        # 启动记忆API服务器
        print()
        print("🚀 步骤 2/3: 启动记忆API服务器...")
        
        if sys.platform == 'win32':
            subprocess.Popen(
                f'start "Memory API Server" python "{self.project_root / "run_memory_api.py"}"',
                shell=True,
                cwd=str(self.project_root)
            )
        else:
            subprocess.Popen(
                [sys.executable, str(self.project_root / "run_memory_api.py")],
                cwd=str(self.project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print("✓ 记忆API服务器已在后台启动")
        print("⏳ 等待服务器启动...")
        time.sleep(3)
        
        # 启动悬浮窗口
        print()
        print("🎨 步骤 3/3: 启动悬浮窗口UI...")
        print()
        print("提示: 在悬浮窗口中:")
        print("  • 点击 '记忆管理' 按钮")
        print("  • 切换到 '检索记忆' 标签")
        print("  • 输入查询关键词进行测试")
        print()
        
        self.run_script("src/advanced_floating_ui.py", "悬浮窗口UI")
    
    def run_test_mode(self):
        """运行测试模式"""
        while True:
            self.show_test_menu()
            choice = self.get_test_choice()
            
            if choice == '0':
                return  # 返回主菜单
            elif choice == '1':
                # 悬浮窗口检索测试
                self.test_with_ui()
            elif choice == '2':
                # 自动检索测试
                self.run_script(
                    "tests/auto_retrieval_test.py",
                    "自动检索测试",
                    ["--conversations", "5", "--messages", "20"]
                )
            elif choice == '3':
                # 交互式测试
                self.run_script(
                    "tests/interactive_memory_test.py",
                    "交互式测试"
                )
            elif choice == '4':
                # 单元测试
                self.run_script(
                    "tests/test_memory_unit.py",
                    "单元测试"
                )
            elif choice == '5':
                # 对话数据测试
                print()
                try:
                    conv = input("要测试多少个对话? (默认3): ").strip() or "3"
                    msg = input("每个对话提取多少消息? (默认20): ").strip() or "20"
                    self.run_script(
                        "tests/test_large_conversations.py",
                        "对话数据测试",
                        ["--conversations", conv, "--messages", msg]
                    )
                except (KeyboardInterrupt, EOFError):
                    print("\n取消")
            elif choice == '6':
                # 记忆对话测试
                self.run_script(
                    "tests/test_memory_with_conversation.py",
                    "记忆对话测试"
                )
            elif choice == '7':
                # 导入ChatGPT记录
                self.run_script(
                    "tests/import_chatgpt_history.py",
                    "导入ChatGPT记录"
                )
            
            # 询问是否继续
            print()
            print("-" * 70)
            try:
                continue_test = input("按 Enter 继续测试，或输入 'q' 返回主菜单: ").strip().lower()
                if continue_test == 'q':
                    return
            except (KeyboardInterrupt, EOFError):
                print()
                return
    
    # ==================== 主运行逻辑 ====================
    
    def run(self):
        """运行启动器"""
        try:
            self.print_banner()
            
            while True:
                self.show_mode_menu()
                mode = self.get_mode_choice()
                
                if mode == '0':
                    print("再见！")
                    break
                elif mode == '1':
                    # 系统启动模式
                    self.run_startup_mode()
                elif mode == '2':
                    # 测试模式
                    self.run_test_mode()
                
                # 如果不是退出，继续循环显示主菜单
                if mode != '0':
                    print()
                    print("=" * 70)
                    try:
                        input("按 Enter 返回主菜单...")
                    except (KeyboardInterrupt, EOFError):
                        print("\n再见！")
                        break
            
        except KeyboardInterrupt:
            print("\n用户取消")
        except Exception as e:
            print(f"\n[错误] 程序异常: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    launcher = CAFALauncher()
    launcher.run()

if __name__ == "__main__":
    main()
