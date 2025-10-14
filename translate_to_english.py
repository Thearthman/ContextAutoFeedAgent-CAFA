#!/usr/bin/env python3
"""
Batch translation script to convert Chinese text to English in all project files
"""

import os
import re
from pathlib import Path

# Translation dictionary for common terms
TRANSLATIONS = {
    # Common phrases
    "启动": "Starting",
    "初始化": "Initializing",
    "加载": "Loading",
    "配置": "Configuration",
    "提供商": "Provider",
    "模型": "Model",
    "未设置": "Not set",
    "已设置": "Set",
    "警告": "Warning",
    "错误": "Error",
    "成功": "Success",
    "失败": "Failed",
    "完成": "Completed",
    
    # Service related
    "服务器": "Server",
    "客户端": "Client",
    "服务": "Service",
    "准备就绪": "Ready",
    "监听": "Listening on",
    "运行": "Running",
    
    # Memory related
    "记忆": "Memory",
    "存储": "Storage/Store",
    "检索": "Retrieval/Search",
    "衰减": "Decay",
    "权重": "Weight",
    "重要性": "Importance",
    "相似度": "Similarity",
    
    # LLM related
    "生成": "Generation/Generate",
    "对话": "Conversation",
    "历史": "History",
    "上下文": "Context",
    "提示词": "Prompt",
    "响应": "Response",
    
    # Status
    "健康检查": "Health check",
    "统计": "Statistics",
    "状态": "Status",
    
    # Actions
    "添加": "Add",
    "删除": "Delete",
    "更新": "Update",
    "清除": "Clear",
    "搜索": "Search",
    "查询": "Query",
    
    # UI related
    "发送": "Send",
    "清空": "Clear",
    "置顶": "Pin",
    "取消置顶": "Unpin",
    
    # Common messages
    "你好": "Hello",
    "谢谢": "Thank you",
    "请稍等": "Please wait",
    "正在处理": "Processing",
}

def find_chinese_files(directory="."):
    """Find all files that might contain Chinese characters"""
    chinese_files = []
    
    # File extensions to check
    extensions = ['.py', '.md', '.txt', '.json']
    
    for root, dirs, files in os.walk(directory):
        # Skip venv, __pycache__, .git
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check if contains Chinese characters
                        if re.search(r'[\u4e00-\u9fff]', content):
                            chinese_files.append(filepath)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return chinese_files

def analyze_file(filepath):
    """Analyze a file and show Chinese content"""
    print(f"\n{'='*80}")
    print(f"File: {filepath}")
    print('='*80)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        chinese_lines = []
        for i, line in enumerate(lines, 1):
            if re.search(r'[\u4e00-\u9fff]', line):
                chinese_lines.append((i, line.strip()))
        
        if chinese_lines:
            print(f"Found {len(chinese_lines)} lines with Chinese:")
            for line_no, content in chinese_lines[:10]:  # Show first 10
                print(f"  Line {line_no}: {content[:100]}")
            if len(chinese_lines) > 10:
                print(f"  ... and {len(chinese_lines) - 10} more lines")
        
        return len(chinese_lines)
    
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    print("🔍 Scanning for files with Chinese content...")
    print("="*80)
    
    chinese_files = find_chinese_files(".")
    
    if not chinese_files:
        print("\n✅ No files with Chinese content found!")
        return
    
    print(f"\n📋 Found {len(chinese_files)} files with Chinese content:\n")
    
    total_lines = 0
    for filepath in sorted(chinese_files):
        count = analyze_file(filepath)
        total_lines += count
    
    print(f"\n{'='*80}")
    print(f"📊 Summary:")
    print(f"   Total files: {len(chinese_files)}")
    print(f"   Total lines with Chinese: {total_lines}")
    print(f"{'='*80}")
    
    print("\n💡 Next steps:")
    print("   1. Review the files listed above")
    print("   2. Update Chinese strings to English manually or with find-replace")
    print("   3. Test the code after changes")
    
    # Generate a list for easy copying
    print("\n📝 File list (for reference):")
    for f in sorted(chinese_files):
        print(f"   - {f}")

if __name__ == "__main__":
    main()

