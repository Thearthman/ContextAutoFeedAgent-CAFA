#!/usr/bin/env python3
"""
快速启动器 - 一键启动ContextAutoFeedAgent-CAFA
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python():
    """检查Python环境"""
    try:
        version = sys.version_info
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    except:
        print("[ERROR] Python环境异常")
        return False

def check_files():
    """检查必要文件"""
    required_files = [
        "src/enhanced_floating_ui.py",
        "requirements.txt"
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
        else:
            print(f"[OK] {file_path}")
    
    if missing:
        print(f"[ERROR] 缺少文件: {', '.join(missing)}")
        return False
    
    return True

def check_servers():
    """检查服务器状态"""
    servers = {
        "本地模型": "http://localhost:5000/health",
        "在线API": "http://localhost:5001/health"
    }
    
    running_servers = []
    
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"[OK] {name}服务器: 运行中")
                running_servers.append(name)
            else:
                print(f"[ERROR] {name}服务器: 异常")
        except:
            print(f"[NO] {name}服务器: 未运行")
    
    return running_servers

def start_ui():
    """启动UI"""
    print("\n启动UI界面...")
    
    try:
        # 启动UI
        process = subprocess.Popen([sys.executable, "src/enhanced_floating_ui.py"])
        print("[OK] UI界面已启动")
        
        # 等待用户操作
        print("\n使用提示:")
        print("   - 在UI中点击 'Switch API' 可以切换API服务")
        print("   - 按 Ctrl+C 停止程序")
        
        # 保持运行
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止...")
            process.terminate()
            
    except Exception as e:
        print(f"[ERROR] 启动UI失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("ContextAutoFeedAgent-CAFA 快速启动器")
    print("=" * 50)
    
    # 检查环境
    if not check_python():
        return
    
    print("\n检查文件...")
    if not check_files():
        return
    
    print("\n检查服务器状态...")
    running_servers = check_servers()
    
    if not running_servers:
        print("\n警告: 未检测到运行中的服务器")
        print("建议:")
        print("   1. 运行 python smart_launcher_v2.py 启动完整服务")
        print("   2. 或手动启动服务器后重新运行此程序")
        
        choice = input("\n是否继续启动UI? (y/n): ").lower().strip()
        if choice != 'y':
            print("再见！")
            return
    
    # 启动UI
    start_ui()

if __name__ == "__main__":
    main()