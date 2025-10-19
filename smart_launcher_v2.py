#!/usr/bin/env python3
"""
智能一键启动程序 - ContextAutoFeedAgent-CAFA
自动检测和启动所有必要的服务
"""

import os
import sys
import time
import subprocess
import requests
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional

class SmartLauncher:
    """智能启动器"""
    
    def __init__(self):
        self.services = {
            "local_model": {
                "name": "本地模型服务器",
                "script": "src/model_server.py",
                "port": 5000,
                "health_url": "http://localhost:5000/health",
                "required": False,
                "running": False
            },
            "online_api": {
                "name": "在线API服务器", 
                "script": "src/online_model_server.py",
                "port": 5001,
                "health_url": "http://localhost:5001/health",
                "required": False,
                "running": False
            },
            "memory_api": {
                "name": "内存API服务",
                "script": "run_memory_api.py", 
                "port": 8000,
                "health_url": "http://localhost:8000/docs",
                "required": False,
                "running": False
            },
            "floating_ui": {
                "name": "浮动UI界面",
                "script": "src/enhanced_floating_ui.py",
                "port": None,
                "health_url": None,
                "required": True,
                "running": False
            }
        }
        
        self.processes = {}
        self.running = True
        
    def print_banner(self):
        """打印启动横幅"""
        print("=" * 60)
        print("ContextAutoFeedAgent-CAFA 智能启动器")
        print("=" * 60)
        print("功能特性:")
        print("   - 自动检测服务状态")
        print("   - 智能选择启动服务")
        print("   - 一键启动所有组件")
        print("   - 实时状态监控")
        print("=" * 60)
        
    def check_dependencies(self) -> bool:
        """检查依赖文件"""
        print("\n检查依赖文件...")
        
        required_files = [
            "requirements.txt",
            "src/enhanced_floating_ui.py",
            "run_memory_api.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            else:
                print(f"   [OK] {file_path}")
        
        if missing_files:
            print(f"\n[ERROR] 缺少必要文件:")
            for file_path in missing_files:
                print(f"   - {file_path}")
            return False
            
        return True
    
    def check_service_status(self, service_name: str) -> bool:
        """检查服务状态"""
        service = self.services[service_name]
        
        if service["health_url"] is None:
            return False
            
        try:
            response = requests.get(service["health_url"], timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def detect_available_services(self) -> List[str]:
        """检测可用的服务"""
        print("\n检测服务状态...")
        
        available_services = []
        
        for service_name, service_info in self.services.items():
            if service_name == "floating_ui":
                # UI不需要检测，直接可用
                available_services.append(service_name)
                print(f"   [OK] {service_info['name']}: 可用")
                continue
                
            is_running = self.check_service_status(service_name)
            service_info["running"] = is_running
            
            if is_running:
                print(f"   [OK] {service_info['name']}: 已运行 (端口{service_info['port']})")
                available_services.append(service_name)
            else:
                print(f"   [NO] {service_info['name']}: 未运行")
                
        return available_services
    
    def check_api_key_config(self) -> Dict[str, bool]:
        """检查API Key配置"""
        print("\n检查API Key配置...")
        
        api_key_status = {
            "env_vars": False,
            "config_file": False,
            "auto_detected": False
        }
        
        # 检查环境变量
        env_keys = ["OPENAI_API_KEY", "LLM_API_KEY", "API_KEY", "OPENAI_KEY"]
        for key in env_keys:
            if os.getenv(key):
                api_key_status["env_vars"] = True
                print(f"   [OK] 环境变量 {key}: 已设置")
                break
        else:
            print(f"   [NO] 环境变量: 未设置")
        
        # 检查配置文件
        config_files = ["api_config.json", ".env", "config.json"]
        for config_file in config_files:
            if os.path.exists(config_file):
                api_key_status["config_file"] = True
                print(f"   [OK] 配置文件 {config_file}: 存在")
                break
        else:
            print(f"   [NO] 配置文件: 不存在")
        
        api_key_status["auto_detected"] = api_key_status["env_vars"] or api_key_status["config_file"]
        
        return api_key_status
    
    def start_service(self, service_name: str) -> bool:
        """启动服务"""
        service = self.services[service_name]
        
        if not os.path.exists(service["script"]):
            print(f"[ERROR] 脚本文件不存在: {service['script']}")
            return False
        
        try:
            print(f"启动 {service['name']}...")
            process = subprocess.Popen(
                [sys.executable, service["script"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = process
            service["running"] = True
            
            # 等待服务启动
            if service["health_url"]:
                self.wait_for_service(service_name, timeout=30)
            
            print(f"[OK] {service['name']} 启动成功")
            return True
            
        except Exception as e:
            print(f"[ERROR] 启动 {service['name']} 失败: {e}")
            return False
    
    def wait_for_service(self, service_name: str, timeout: int = 30):
        """等待服务启动"""
        service = self.services[service_name]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_service_status(service_name):
                return True
            time.sleep(1)
        
        return False
    
    def show_service_menu(self, available_services: List[str], api_key_status: Dict[str, bool]):
        """显示服务选择菜单"""
        print("\n服务选择菜单:")
        print("=" * 40)
        
        print("1. 启动所有服务 (推荐)")
        print("2. 智能启动 (根据配置自动选择)")
        print("3. 仅启动UI界面")
        print("4. 自定义选择服务")
        print("5. 退出")
        
        print("=" * 40)
        
        while True:
            try:
                choice = input("请选择 (1-5): ").strip()
                
                if choice == "1":
                    return "all"
                elif choice == "2":
                    return "smart"
                elif choice == "3":
                    return "ui_only"
                elif choice == "4":
                    return "custom"
                elif choice == "5":
                    return "exit"
                else:
                    print("[ERROR] 无效选择，请输入 1-5")
                    
            except KeyboardInterrupt:
                print("\n用户取消")
                return "exit"
    
    def smart_start(self, api_key_status: Dict[str, bool]):
        """智能启动策略"""
        print("\n执行智能启动策略...")
        
        services_to_start = []
        
        # 总是启动UI
        services_to_start.append("floating_ui")
        
        # 根据API Key状态决定启动哪个后端服务
        if api_key_status["auto_detected"]:
            print("   检测到API Key，优先启动在线API服务器")
            services_to_start.append("online_api")
        else:
            print("   未检测到API Key，启动本地模型服务器")
            services_to_start.append("local_model")
        
        # 启动内存API (可选)
        if os.path.exists("run_memory_api.py"):
            services_to_start.append("memory_api")
        
        return services_to_start
    
    def custom_service_selection(self, available_services: List[str]):
        """自定义服务选择"""
        print("\n自定义服务选择:")
        print("=" * 30)
        
        service_list = list(self.services.keys())
        selected_services = []
        
        for i, service_name in enumerate(service_list, 1):
            service_info = self.services[service_name]
            status = "[OK] 已运行" if service_info["running"] else "[NO] 未运行"
            print(f"{i}. {service_info['name']} - {status}")
        
        print("=" * 30)
        
        while True:
            try:
                choice = input("请选择要启动的服务 (输入数字，多个用逗号分隔): ").strip()
                
                if not choice:
                    continue
                
                # 解析选择
                selections = [s.strip() for s in choice.split(",")]
                selected_services = []
                
                for sel in selections:
                    try:
                        idx = int(sel) - 1
                        if 0 <= idx < len(service_list):
                            selected_services.append(service_list[idx])
                        else:
                            print(f"[ERROR] 无效选择: {sel}")
                            break
                    except ValueError:
                        print(f"[ERROR] 无效输入: {sel}")
                        break
                else:
                    break
                    
            except KeyboardInterrupt:
                print("\n用户取消")
                return []
        
        return selected_services
    
    def start_selected_services(self, services_to_start: List[str]):
        """启动选定的服务"""
        print(f"\n启动选定的服务...")
        
        success_count = 0
        
        for service_name in services_to_start:
            if service_name == "floating_ui":
                # UI最后启动
                continue
                
            if self.services[service_name]["running"]:
                print(f"[OK] {self.services[service_name]['name']} 已在运行")
                success_count += 1
            else:
                if self.start_service(service_name):
                    success_count += 1
        
        # 最后启动UI
        if "floating_ui" in services_to_start:
            print(f"\n启动UI界面...")
            if self.start_service("floating_ui"):
                success_count += 1
        
        print(f"\n启动结果: {success_count}/{len(services_to_start)} 个服务启动成功")
        
        if success_count > 0:
            print("\n启动完成！")
            print("提示:")
            print("   - 在UI中点击 'Switch API' 可以切换API服务")
            print("   - 按 Ctrl+C 可以停止所有服务")
            
            # 保持运行状态
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在停止所有服务...")
                self.stop_all_services()
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n停止所有服务...")
        
        for service_name, process in self.processes.items():
            try:
                if process.poll() is None:  # 进程仍在运行
                    print(f"   停止 {self.services[service_name]['name']}...")
                    process.terminate()
                    process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        
        print("[OK] 所有服务已停止")
    
    def run(self):
        """运行启动器"""
        try:
            self.print_banner()
            
            # 检查依赖
            if not self.check_dependencies():
                print("\n[ERROR] 依赖检查失败，请确保所有必要文件存在")
                return
            
            # 检测服务状态
            available_services = self.detect_available_services()
            
            # 检查API Key配置
            api_key_status = self.check_api_key_config()
            
            # 显示菜单
            choice = self.show_service_menu(available_services, api_key_status)
            
            if choice == "exit":
                print("再见！")
                return
            
            # 根据选择启动服务
            if choice == "all":
                services_to_start = list(self.services.keys())
            elif choice == "smart":
                services_to_start = self.smart_start(api_key_status)
            elif choice == "ui_only":
                services_to_start = ["floating_ui"]
            elif choice == "custom":
                services_to_start = self.custom_service_selection(available_services)
            else:
                return
            
            if not services_to_start:
                print("[ERROR] 未选择任何服务")
                return
            
            # 启动服务
            self.start_selected_services(services_to_start)
            
        except KeyboardInterrupt:
            print("\n用户取消")
        except Exception as e:
            print(f"\n[ERROR] 启动器运行错误: {e}")
        finally:
            self.stop_all_services()

def main():
    """主函数"""
    launcher = SmartLauncher()
    launcher.run()

if __name__ == "__main__":
    main()