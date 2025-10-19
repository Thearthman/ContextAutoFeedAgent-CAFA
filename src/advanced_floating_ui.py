#!/usr/bin/env python3
"""
完整增强版浮动UI - 集成API切换和记忆功能
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import time
from datetime import datetime
from typing import Optional, Dict, List

class AdvancedFloatingChatUI:
    """完整增强版浮动聊天UI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CAFA - Context Auto Feed Agent")
        
        # 颜色主题
        self.bg_color = "#1e1e1e"
        self.text_color = "#e0e0e0"
        self.accent_color = "#007acc"
        self.success_color = "#4ec9b0"
        self.error_color = "#f48771"
        self.memory_color = "#ce9178"
        
        # 服务器配置
        self.server_url = "http://localhost:5001"  # 默认在线API服务器
        self.memory_url = "http://localhost:8000"   # 记忆API服务器
        
        # 服务器信息
        self.server_info = {}
        self.memory_enabled = False
        
        # 对话历史
        self.conversation_history = []
        
        # 初始化UI
        self._setup_ui()
        
        # 检查服务器状态
        self._check_all_services()
        
    def _setup_ui(self):
        """设置UI界面"""
        # 设置窗口大小和位置
        window_width = 450
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 20
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=self.bg_color)
        
        # 设置窗口属性
        self.root.attributes('-topmost', True)
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部状态栏
        self._create_status_bar(main_frame)
        
        # 控制按钮区域
        self._create_control_buttons(main_frame)
        
        # 聊天显示区域
        self._create_chat_display(main_frame)
        
        # 输入区域
        self._create_input_area(main_frame)
        
    def _create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = tk.Frame(parent, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = tk.Label(
            status_frame,
            text="CAFA - Context Auto Feed Agent",
            font=("Arial", 14, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 10))
        
        # 服务状态框架
        services_frame = tk.Frame(status_frame, bg=self.bg_color)
        services_frame.pack(fill=tk.X)
        
        # API服务器状态
        self.api_status_label = tk.Label(
            services_frame,
            text="API: 检测中...",
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.api_status_label.pack(side=tk.LEFT, padx=5)
        
        # 记忆服务状态
        self.memory_status_label = tk.Label(
            services_frame,
            text="记忆: 检测中...",
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.memory_status_label.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        separator = tk.Frame(status_frame, height=1, bg="#3e3e3e")
        separator.pack(fill=tk.X, pady=10)
        
    def _create_control_buttons(self, parent):
        """创建控制按钮"""
        control_frame = tk.Frame(parent, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API切换按钮
        self.api_switch_btn = tk.Button(
            control_frame,
            text="切换API",
            command=self._show_api_switch_dialog,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.api_switch_btn.pack(side=tk.LEFT, padx=5)
        
        # 记忆管理按钮
        self.memory_btn = tk.Button(
            control_frame,
            text="记忆管理",
            command=self._show_memory_dialog,
            bg=self.memory_color,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.memory_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空对话按钮
        clear_btn = tk.Button(
            control_frame,
            text="清空",
            command=self._clear_chat,
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
    def _create_chat_display(self, parent):
        """创建聊天显示区域"""
        # 创建框架
        chat_frame = tk.Frame(parent, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动文本框
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签
        self.chat_display.tag_config("user", foreground=self.accent_color, font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground=self.success_color, font=("Arial", 10, "bold"))
        self.chat_display.tag_config("system", foreground=self.error_color, font=("Arial", 9, "italic"))
        self.chat_display.tag_config("memory", foreground=self.memory_color, font=("Arial", 9, "italic"))
        
        # 显示欢迎消息
        self._display_welcome_message()
        
    def _create_input_area(self, parent):
        """创建输入区域"""
        input_frame = tk.Frame(parent, bg=self.bg_color)
        input_frame.pack(fill=tk.X)
        
        # 输入框
        self.input_text = tk.Text(
            input_frame,
            height=3,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.input_text.pack(fill=tk.X, pady=(0, 10))
        
        # 绑定快捷键
        self.input_text.bind("<Control-Return>", lambda e: self._send_message())
        
        # 按钮框架
        button_frame = tk.Frame(input_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        # 发送按钮
        send_btn = tk.Button(
            button_frame,
            text="发送 (Ctrl+Enter)",
            command=self._send_message,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        send_btn.pack(side=tk.RIGHT)
        
    def _display_welcome_message(self):
        """显示欢迎消息"""
        welcome_msg = """
=================================
欢迎使用 CAFA (Context Auto Feed Agent)
=================================

功能特性:
• 智能API切换 - 点击"切换API"按钮选择服务
• 记忆功能 - 点击"记忆管理"查看和管理记忆
• 上下文感知对话
• 实时状态监控

快捷键:
• Ctrl+Enter - 发送消息

开始对话吧！
=================================
"""
        self.chat_display.insert(tk.END, welcome_msg, "system")
        self.chat_display.see(tk.END)
        
    def _check_all_services(self):
        """检查所有服务状态"""
        # 在后台线程中检查
        threading.Thread(target=self._check_services_thread, daemon=True).start()
        
    def _check_services_thread(self):
        """检查服务状态的线程"""
        # 检查API服务器
        api_ok = self._check_api_server()
        
        # 检查记忆服务器
        memory_ok = self._check_memory_server()
        
        # 更新UI
        self.root.after(0, self._update_service_status, api_ok, memory_ok)
        
    def _check_api_server(self):
        """检查API服务器"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.server_info = response.json()
                return True
        except:
            pass
        return False
        
    def _check_memory_server(self):
        """检查记忆服务器"""
        try:
            response = requests.get(f"{self.memory_url}/docs", timeout=5)
            if response.status_code == 200:
                self.memory_enabled = True
                return True
        except:
            pass
        self.memory_enabled = False
        return False
        
    def _update_service_status(self, api_ok, memory_ok):
        """更新服务状态显示"""
        # 更新API状态
        if api_ok:
            model = self.server_info.get('model', 'unknown')
            provider = self.server_info.get('provider', 'unknown')
            self.api_status_label.config(
                text=f"API: {provider}/{model}",
                fg=self.success_color
            )
        else:
            self.api_status_label.config(
                text="API: 未连接",
                fg=self.error_color
            )
            
        # 更新记忆状态
        if memory_ok:
            self.memory_status_label.config(
                text="记忆: 已启用",
                fg=self.success_color
            )
        else:
            self.memory_status_label.config(
                text="记忆: 未启用",
                fg=self.error_color
            )
            
    def _show_api_switch_dialog(self):
        """显示API切换对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("API服务切换")
        dialog.geometry("550x500")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        
        # 居中对话框
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 主框架
        main_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="选择API服务",
            font=("Arial", 16, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # 检测结果框架
        detection_frame = tk.LabelFrame(
            main_frame,
            text="服务检测结果",
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor=tk.NW
        )
        detection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 检测各个服务
        services = self._detect_all_services()
        
        for service in services:
            service_frame = tk.Frame(detection_frame, bg=self.bg_color)
            service_frame.pack(fill=tk.X, padx=10, pady=5)
            
            status_symbol = "●" if service['available'] else "○"
            status_color = self.success_color if service['available'] else self.error_color
            
            status_label = tk.Label(
                service_frame,
                text=f"{status_symbol} {service['name']}: {service['status']}",
                font=("Arial", 10),
                fg=status_color,
                bg=self.bg_color
            )
            status_label.pack(anchor=tk.W)
            
        # 选择框架
        selection_frame = tk.LabelFrame(
            main_frame,
            text="选择要使用的API",
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor=tk.NW
        )
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # API选项
        self.selected_api_var = tk.StringVar()
        
        for i, service in enumerate(services):
            if not service.get('selectable', True):
                continue
                
            radio_frame = tk.Frame(selection_frame, bg=self.bg_color)
            radio_frame.pack(fill=tk.X, padx=10, pady=5)
            
            radio = tk.Radiobutton(
                radio_frame,
                text=service['name'],
                variable=self.selected_api_var,
                value=service['url'],
                font=("Arial", 11),
                fg=self.text_color,
                bg=self.bg_color,
                selectcolor=self.accent_color,
                activebackground=self.bg_color,
                activeforeground=self.text_color,
                state="normal" if service['available'] else "disabled"
            )
            radio.pack(anchor=tk.W)
            
            # 描述
            desc_label = tk.Label(
                radio_frame,
                text=f"  {service['description']}",
                font=("Arial", 9),
                fg="#858585" if service['available'] else "#666666",
                bg=self.bg_color
            )
            desc_label.pack(anchor=tk.W)
            
            # 设置默认选择
            if i == 0 and service['available']:
                self.selected_api_var.set(service['url'])
                
        # 按钮框架
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=dialog.destroy,
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # 确定按钮
        confirm_btn = tk.Button(
            button_frame,
            text="确定",
            command=lambda: self._perform_api_switch(dialog),
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)
        
    def _detect_all_services(self):
        """检测所有服务"""
        services = []
        
        # 1. 本地模型服务器 (端口5000)
        local_ok = False
        try:
            response = requests.get("http://localhost:5000/health", timeout=3)
            local_ok = response.status_code == 200
        except:
            pass
            
        services.append({
            'name': '本地模型服务器 (Gemma)',
            'url': 'http://localhost:5000',
            'status': '运行中' if local_ok else '未运行',
            'available': local_ok,
            'description': '使用本地Gemma模型，无需API Key',
            'selectable': True
        })
        
        # 2. 在线API服务器 (端口5001)
        online_ok = False
        try:
            response = requests.get("http://localhost:5001/health", timeout=3)
            online_ok = response.status_code == 200
        except:
            pass
            
        services.append({
            'name': '在线API服务器 (OpenAI)',
            'url': 'http://localhost:5001',
            'status': '运行中' if online_ok else '未运行',
            'available': online_ok,
            'description': '使用OpenAI API，需要API Key',
            'selectable': True
        })
        
        # 3. 记忆服务器 (端口8000)
        memory_ok = False
        try:
            response = requests.get("http://localhost:8000/docs", timeout=3)
            memory_ok = response.status_code == 200
        except:
            pass
            
        services.append({
            'name': '记忆服务器',
            'url': 'http://localhost:8000',
            'status': '运行中' if memory_ok else '未运行',
            'available': memory_ok,
            'description': '提供记忆存储和检索功能',
            'selectable': False
        })
        
        return services
        
    def _perform_api_switch(self, dialog):
        """执行API切换"""
        selected_url = self.selected_api_var.get()
        
        if not selected_url:
            messagebox.showwarning("未选择", "请选择一个API服务！")
            return
            
        # 更新服务器URL
        self.server_url = selected_url
        
        # 关闭对话框
        dialog.destroy()
        
        # 重新检查服务状态
        self._check_all_services()
        
        # 显示切换成功消息
        self._display_system_message(f"已切换到: {selected_url}")
        
    def _show_memory_dialog(self):
        """显示记忆管理对话框"""
        if not self.memory_enabled:
            messagebox.showwarning(
                "记忆功能未启用",
                "记忆服务器未运行！\n\n请启动记忆服务器:\npython run_memory_api.py"
            )
            return
            
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("记忆管理")
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        
        # 居中对话框
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 主框架
        main_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="记忆管理",
            font=("Arial", 16, "bold"),
            fg=self.memory_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # 创建Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 配置样式
        style = ttk.Style()
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color)
        
        # 标签页1: 存储记忆
        store_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(store_frame, text="存储记忆")
        
        store_label = tk.Label(
            store_frame,
            text="输入要存储的记忆:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        store_label.pack(anchor=tk.W, pady=10)
        
        self.memory_input = scrolledtext.ScrolledText(
            store_frame,
            height=10,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            wrap=tk.WORD
        )
        self.memory_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        store_btn = tk.Button(
            store_frame,
            text="存储",
            command=self._store_memory,
            bg=self.memory_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        store_btn.pack()
        
        # 标签页2: 检索记忆
        recall_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(recall_frame, text="检索记忆")
        
        recall_label = tk.Label(
            recall_frame,
            text="输入查询关键词:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        recall_label.pack(anchor=tk.W, pady=10)
        
        search_frame = tk.Frame(recall_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.memory_query = tk.Entry(
            search_frame,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            relief=tk.FLAT
        )
        self.memory_query.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        search_btn = tk.Button(
            search_frame,
            text="检索",
            command=self._recall_memory,
            bg=self.memory_color,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            cursor="hand2"
        )
        search_btn.pack(side=tk.RIGHT)
        
        self.memory_results = scrolledtext.ScrolledText(
            recall_frame,
            height=12,
            font=("Arial", 9),
            bg="#2d2d2d",
            fg=self.text_color,
            wrap=tk.WORD
        )
        self.memory_results.pack(fill=tk.BOTH, expand=True)
        
        # 标签页3: 记忆统计
        stats_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(stats_frame, text="记忆统计")
        
        self.memory_stats = scrolledtext.ScrolledText(
            stats_frame,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            wrap=tk.WORD
        )
        self.memory_stats.pack(fill=tk.BOTH, expand=True, pady=10)
        
        refresh_stats_btn = tk.Button(
            stats_frame,
            text="刷新统计",
            command=self._refresh_memory_stats,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        refresh_stats_btn.pack()
        
        # 初始化统计
        self._refresh_memory_stats()
        
    def _store_memory(self):
        """存储记忆"""
        memory_text = self.memory_input.get("1.0", tk.END).strip()
        
        if not memory_text:
            messagebox.showwarning("输入为空", "请输入要存储的记忆内容！")
            return
            
        try:
            response = requests.post(
                f"{self.memory_url}/store",
                params={"text": memory_text},
                timeout=5
            )
            
            if response.status_code == 200:
                messagebox.showinfo("成功", "记忆已成功存储！")
                self.memory_input.delete("1.0", tk.END)
            else:
                messagebox.showerror("错误", f"存储失败: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("错误", f"存储异常: {str(e)}")
            
    def _recall_memory(self):
        """检索记忆"""
        query = self.memory_query.get().strip()
        
        if not query:
            messagebox.showwarning("输入为空", "请输入查询关键词！")
            return
            
        try:
            response = requests.get(
                f"{self.memory_url}/recall",
                params={"query": query},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get("matches", [])
                
                self.memory_results.delete("1.0", tk.END)
                
                if matches:
                    self.memory_results.insert(tk.END, f"找到 {len(matches)} 个匹配记忆:\n\n")
                    
                    for i, match in enumerate(matches, 1):
                        text = match.get('text', 'N/A')
                        similarity = match.get('similarity', 0)
                        self.memory_results.insert(
                            tk.END,
                            f"{i}. [{similarity:.3f}] {text}\n\n"
                        )
                else:
                    self.memory_results.insert(tk.END, "未找到匹配的记忆。")
            else:
                messagebox.showerror("错误", f"检索失败: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("错误", f"检索异常: {str(e)}")
            
    def _refresh_memory_stats(self):
        """刷新记忆统计"""
        self.memory_stats.delete("1.0", tk.END)
        
        stats_text = f"""
记忆服务统计信息
=================================

服务地址: {self.memory_url}
状态: {'已启用' if self.memory_enabled else '未启用'}

API端点:
• 存储记忆: POST /store
• 检索记忆: GET /recall
• 记忆衰减: POST /decay

文档:
• Swagger UI: {self.memory_url}/docs
• ReDoc: {self.memory_url}/redoc

功能特性:
✓ 智能语义搜索
✓ 记忆权重管理
✓ 自动记忆衰减
✓ 相似度匹配

=================================
"""
        self.memory_stats.insert(tk.END, stats_text)
        
    def _send_message(self):
        """发送消息"""
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message:
            return
            
        # 清空输入框
        self.input_text.delete("1.0", tk.END)
        
        # 显示用户消息
        self._display_message("用户", message, "user")
        
        # 在后台线程中发送请求
        threading.Thread(
            target=self._send_request_thread,
            args=(message,),
            daemon=True
        ).start()
        
    def _send_request_thread(self, message):
        """发送请求的线程"""
        try:
            # 如果启用了记忆，先检索相关记忆
            memory_context = ""
            if self.memory_enabled:
                try:
                    response = requests.get(
                        f"{self.memory_url}/recall",
                        params={"query": message},
                        timeout=3
                    )
                    if response.status_code == 200:
                        data = response.json()
                        matches = data.get("matches", [])
                        if matches:
                            memory_texts = [m.get('text', '') for m in matches[:3]]
                            memory_context = "\n相关记忆: " + "; ".join(memory_texts)
                            self.root.after(0, self._display_memory_context, memory_context)
                except:
                    pass
            
            # 发送到API服务器
            response = requests.post(
                f"{self.server_url}/chat",
                json={
                    "message": message + memory_context,
                    "conversation_id": "default"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data.get('response', '无响应')
                
                # 显示助手消息
                self.root.after(0, self._display_message, "助手", assistant_message, "assistant")
                
                # 存储到记忆
                if self.memory_enabled:
                    try:
                        requests.post(
                            f"{self.memory_url}/store",
                            params={"text": f"Q:{message} A:{assistant_message}"},
                            timeout=3
                        )
                    except:
                        pass
            else:
                error_msg = f"请求失败: HTTP {response.status_code}"
                self.root.after(0, self._display_system_message, error_msg)
                
        except requests.exceptions.Timeout:
            self.root.after(0, self._display_system_message, "请求超时")
        except requests.exceptions.ConnectionError:
            self.root.after(0, self._display_system_message, "无法连接到服务器")
        except Exception as e:
            self.root.after(0, self._display_system_message, f"错误: {str(e)}")
            
    def _display_message(self, sender, message, tag):
        """显示消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.see(tk.END)
        
    def _display_system_message(self, message):
        """显示系统消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"系统: {message}\n", "system")
        self.chat_display.see(tk.END)
        
    def _display_memory_context(self, context):
        """显示记忆上下文"""
        self.chat_display.insert(tk.END, f"{context}\n", "memory")
        self.chat_display.see(tk.END)
        
    def _clear_chat(self):
        """清空聊天"""
        self.chat_display.delete("1.0", tk.END)
        self._display_welcome_message()
        
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    print("[INFO] Starting Advanced Floating UI...")
    print("[INFO] Features: API Switch + Memory Management")
    
    app = AdvancedFloatingChatUI()
    app.run()

if __name__ == "__main__":
    main()
