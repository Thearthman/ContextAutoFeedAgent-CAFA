
#!/usr/bin/env python3
"""
一键启动程序 - ContextAutoFeedAgent-CAFA
"""

import os
import sys
import subprocess
import time
import requests

def main():
    """主函数"""
    print("=" * 60)
    print("ContextAutoFeedAgent-CAFA 一键启动程序")
    print("=" * 60)
    
    # 检查Python环境
    print("检查Python环境...")
    try:
        version = sys.version_info
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    except:
        print("[ERROR] Python环境异常")
        return
    
    # 检查必要文件
    print("\n检查文件...")
    required_files = [
        "src/enhanced_floating_ui.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] 缺少文件: {file_path}")
            return
    
    # 检查服务器状态
    print("\n检查服务器状态...")
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
    
    # 显示启动选项
    print("\n启动选项:")
    print("1. 启动UI界面 (推荐)")
    print("2. 启动智能启动器")
    print("3. 启动快速启动器")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == "1":
                start_ui()
                break
            elif choice == "2":
                start_smart_launcher()
                break
            elif choice == "3":
                start_quick_launcher()
                break
            elif choice == "4":
                print("再见！")
                break
            else:
                print("[ERROR] 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print("\n用户取消")
            break

def start_ui():
    """启动UI界面"""
    print("\n启动UI界面...")
    
    try:
        process = subprocess.Popen([sys.executable, "src/enhanced_floating_ui.py"])
        print("[OK] UI界面已启动")
        
        print("\n使用提示:")
        print("   - 在UI中点击 'Switch API' 可以切换API服务")
        print("   - 按 Ctrl+C 停止程序")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止...")
            process.terminate()
            
    except Exception as e:
        print(f"[ERROR] 启动UI失败: {e}")

def start_smart_launcher():
    """启动智能启动器"""
    print("\n启动智能启动器...")
    
    try:
        if os.path.exists("smart_launcher_v2.py"):
            subprocess.run([sys.executable, "smart_launcher_v2.py"])
        else:
            print("[ERROR] 智能启动器文件不存在")
    except Exception as e:
        print(f"[ERROR] 启动智能启动器失败: {e}")

def start_quick_launcher():
    """启动快速启动器"""
    print("\n启动快速启动器...")
    
    try:
        if os.path.exists("quick_start.py"):
            subprocess.run([sys.executable, "quick_start.py"])
        else:
            print("[ERROR] 快速启动器文件不存在")
    except Exception as e:
        print(f"[ERROR] 启动快速启动器失败: {e}")

if __name__ == "__main__":
    main()
