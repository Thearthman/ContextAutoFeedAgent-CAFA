#!/usr/bin/env python3
"""
Advanced Floating UI - Integrated API switching and memory features
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import time
from datetime import datetime
from typing import Optional, Dict, List

# Import UI text constants
try:
    from src.ui_text import (MAIN_UI, BUTTONS, MODEL_SELECTION, API_KEY_DIALOG, 
                              MEMORY_DIALOG, MESSAGES, STATUS, CHAT)
except ImportError:
    # Fallback if import fails
    from ui_text import (MAIN_UI, BUTTONS, MODEL_SELECTION, API_KEY_DIALOG,
                         MEMORY_DIALOG, MESSAGES, STATUS, CHAT)


class AdvancedFloatingChatUI:
    """Advanced floating chat UI with full features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(MAIN_UI["title"])
        
        # Color theme
        self.bg_color = "#1e1e1e"
        self.text_color = "#e0e0e0"
        self.accent_color = "#007acc"
        self.success_color = "#4ec9b0"
        self.error_color = "#f48771"
        self.memory_color = "#ce9178"
        
        # Server configuration
        self.server_url = "http://localhost:5001"  # Default online API server
        self.memory_url = "http://localhost:8000"   # Memory API server
        
        # Server information
        self.server_info = {}
        self.memory_enabled = False
        
        # Conversation history
        self.conversation_history = []
        
        # Initialize UI
        self._setup_ui()
        
        # Check server status
        self._check_all_services()
        
    def _setup_ui(self):
        """Setup UI interface"""
        # Set window size and position
        window_width = 450
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - window_width - 20
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=self.bg_color)
        
        # Set window properties
        self.root.attributes('-topmost', True)
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top status bar
        self._create_status_bar(main_frame)
        
        # Control buttons area
        self._create_control_buttons(main_frame)
        
        # Chat display area
        self._create_chat_display(main_frame)
        
        # Input area
        self._create_input_area(main_frame)
        
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            status_frame,
            text=MAIN_UI["title"],
            font=("Arial", 14, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 10))
        
        # Service status frame
        services_frame = tk.Frame(status_frame, bg=self.bg_color)
        services_frame.pack(fill=tk.X)
        
        # API server status
        self.api_status_label = tk.Label(
            services_frame,
            text=STATUS["api_detecting"],
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.api_status_label.pack(side=tk.LEFT, padx=5)
        
        # Memory service status
        self.memory_status_label = tk.Label(
            services_frame,
            text=STATUS["memory_detecting"],
            font=("Arial", 9),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.memory_status_label.pack(side=tk.LEFT, padx=5)
        
        # Separator line
        separator = tk.Frame(status_frame, height=1, bg="#3e3e3e")
        separator.pack(fill=tk.X, pady=10)
        
    def _create_control_buttons(self, parent):
        """Create control buttons"""
        control_frame = tk.Frame(parent, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Select model button
        self.model_select_btn = tk.Button(
            control_frame,
            text=BUTTONS["select_model"],
            command=self._show_model_select_dialog,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.model_select_btn.pack(side=tk.LEFT, padx=5)
        
        # Set API Key button
        self.api_key_btn = tk.Button(
            control_frame,
            text=BUTTONS["set_api"],
            command=self._show_api_key_dialog,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.api_key_btn.pack(side=tk.LEFT, padx=5)
        
        # Memory management button
        self.memory_btn = tk.Button(
            control_frame,
            text=BUTTONS["memory"],
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
        
        # Clear button
        clear_btn = tk.Button(
            control_frame,
            text=BUTTONS["clear"],
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
        """Create chat display area"""
        # Create frame
        chat_frame = tk.Frame(parent, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create scrolled text box
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
        
        # Configure tags
        self.chat_display.tag_config("user", foreground=self.accent_color, font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground=self.success_color, font=("Arial", 10, "bold"))
        self.chat_display.tag_config("system", foreground=self.error_color, font=("Arial", 9, "italic"))
        self.chat_display.tag_config("memory", foreground=self.memory_color, font=("Arial", 9, "italic"))
        
        # Display welcome message
        self._display_welcome_message()
        
    def _create_input_area(self, parent):
        """Create input area"""
        input_frame = tk.Frame(parent, bg=self.bg_color)
        input_frame.pack(fill=tk.X)
        
        # Input box
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
        
        # Bind shortcut key
        self.input_text.bind("<Control-Return>", lambda e: self._send_message())
        
        # Button frame
        button_frame = tk.Frame(input_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        # Send button
        send_btn = tk.Button(
            button_frame,
            text="Send (Ctrl+Enter)",
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
        """Display welcome message"""
        self.chat_display.insert(tk.END, MAIN_UI["welcome_message"], "system")
        self.chat_display.see(tk.END)
        
    def _check_all_services(self):
        """Check all service status"""
        # Check in background thread
        threading.Thread(target=self._check_services_thread, daemon=True).start()
        
    def _check_services_thread(self):
        """Thread for checking service status"""
        # Check API server
        api_ok = self._check_api_server()
        
        # Check memory server
        memory_ok = self._check_memory_server()
        
        # Update UI
        self.root.after(0, self._update_service_status, api_ok, memory_ok)
        
    def _check_api_server(self):
        """Check API server"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.server_info = response.json()
                return True
        except:
            pass
        return False
        
    def _check_memory_server(self):
        """Check memory server"""
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
        """Update service status display"""
        # Update API status
        if api_ok:
            model = self.server_info.get('model', 'unknown')
            provider = self.server_info.get('provider', 'unknown')
            self.api_status_label.config(
                text=STATUS["api_connected"].format(provider=provider, model=model),
                fg=self.success_color
            )
        else:
            self.api_status_label.config(
                text=STATUS["api_not_connected"],
                fg=self.error_color
            )
            
        # Update memory status
        if memory_ok:
            self.memory_status_label.config(
                text=STATUS["memory_enabled"],
                fg=self.success_color
            )
        else:
            self.memory_status_label.config(
                text=STATUS["memory_not_enabled"],
                fg=self.error_color
            )
            
    def _show_api_key_dialog(self):
        """Show API key input dialog"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(API_KEY_DIALOG["title"])
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=API_KEY_DIALOG["title"],
            font=("Arial", 16, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Instruction text
        info_label = tk.Label(
            main_frame,
            text=API_KEY_DIALOG["subtitle"],
            font=("Arial", 10),
            fg="#858585",
            bg=self.bg_color
        )
        info_label.pack(pady=(0, 15))
        
        # API Key input area
        input_frame = tk.LabelFrame(
            main_frame,
            text=API_KEY_DIALOG["input_label"],
            font=("Arial", 11, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor=tk.NW
        )
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # API Key input box
        api_key_entry = tk.Entry(
            input_frame,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg=self.text_color,
            relief=tk.FLAT,
            show="*"  # Hide by default
        )
        api_key_entry.pack(fill=tk.X, padx=10, pady=10)
        
        # Show/Hide key button
        show_var = tk.BooleanVar(value=False)
        
        def toggle_show():
            if show_var.get():
                api_key_entry.config(show="")
                show_btn.config(text=BUTTONS["hide_key"])
            else:
                api_key_entry.config(show="*")
                show_btn.config(text=BUTTONS["show_key"])
        
        show_btn = tk.Button(
            input_frame,
            text=BUTTONS["show_key"],
            command=lambda: [show_var.set(not show_var.get()), toggle_show()],
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=3
        )
        show_btn.pack(padx=10, pady=(0, 10))
        
        # Detection result area
        result_frame = tk.LabelFrame(
            main_frame,
            text=API_KEY_DIALOG["result_label"],
            font=("Arial", 11, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
            labelanchor=tk.NW
        )
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        result_text = scrolledtext.ScrolledText(
            result_frame,
            height=8,
            font=("Arial", 9),
            bg="#2d2d2d",
            fg=self.text_color,
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        result_text.insert(tk.END, API_KEY_DIALOG["initial_text"])
        result_text.config(state=tk.DISABLED)
        
        # Button area
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        # Detect button
        def detect_api_key():
            api_key = api_key_entry.get().strip()
            
            if not api_key:
                messagebox.showwarning(MESSAGES["empty_input"], MESSAGES["enter_api_key"])
                return
            
            # Call detection API
            try:
                response = requests.post(
                    f"{self.server_url}/test_api_key",
                    json={"api_key": api_key},
                    timeout=5
                )
                
                result_text.config(state=tk.NORMAL)
                result_text.delete("1.0", tk.END)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("valid"):
                        provider_name = data.get("provider_display_name", data.get("provider", "unknown"))
                        confidence = data.get("confidence", 0) * 100
                        
                        result_text.insert(tk.END, API_KEY_DIALOG["format_valid"], "success")
                        result_text.insert(tk.END, API_KEY_DIALOG["detected_provider"].format(provider=provider_name))
                        result_text.insert(tk.END, API_KEY_DIALOG["confidence"].format(confidence=confidence))
                        
                        if data.get("description"):
                            result_text.insert(tk.END, API_KEY_DIALOG["description"].format(description=data['description']))
                        
                        if data.get("base_url"):
                            result_text.insert(tk.END, API_KEY_DIALOG["api_url"].format(base_url=data['base_url']))
                        
                        if data.get("default_model"):
                            result_text.insert(tk.END, API_KEY_DIALOG["default_model"].format(model=data['default_model']))
                        
                        if data.get("supported_models"):
                            models = data['supported_models'][:5]
                            result_text.insert(tk.END, API_KEY_DIALOG["supported_models"])
                            for model in models:
                                result_text.insert(tk.END, API_KEY_DIALOG["model_item"].format(model=model))
                            if len(data['supported_models']) > 5:
                                result_text.insert(tk.END, API_KEY_DIALOG["model_count"].format(
                                    count=len(data['supported_models'])))
                        
                        if data.get("warning"):
                            result_text.insert(tk.END, API_KEY_DIALOG["warning"].format(warning=data['warning']), "warning")
                    else:
                        result_text.insert(tk.END, API_KEY_DIALOG["validation_failed"].format(
                            error=data.get('error', 'Unknown error')), "error")
                else:
                    result_text.insert(tk.END, API_KEY_DIALOG["request_failed"].format(
                        status_code=response.status_code), "error")
                
                result_text.config(state=tk.DISABLED)
                
            except requests.exceptions.Timeout:
                messagebox.showerror(MESSAGES["timeout"], MESSAGES["timeout_msg"])
            except requests.exceptions.ConnectionError:
                messagebox.showerror(MESSAGES["connection_failed"], MESSAGES["connection_failed_msg"])
            except Exception as e:
                messagebox.showerror(MESSAGES["error"], MESSAGES["error_occurred"].format(error=str(e)))
        
        detect_btn = tk.Button(
            button_frame,
            text=BUTTONS["detect"],
            command=detect_api_key,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        detect_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text=BUTTONS["cancel"],
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
        
        # Confirm button (Set API Key)
        def set_api_key():
            api_key = api_key_entry.get().strip()
            
            if not api_key:
                messagebox.showwarning(MESSAGES["empty_input"], MESSAGES["enter_api_key"])
                return
            
            try:
                response = requests.post(
                    f"{self.server_url}/set_api_key",
                    json={"api_key": api_key},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        provider_name = data.get("provider_display_name", data.get("provider", "unknown"))
                        messagebox.showinfo(
                            API_KEY_DIALOG["set_success"],
                            API_KEY_DIALOG["set_success"].format(
                                provider=provider_name,
                                model=data.get('model', 'N/A')
                            )
                        )
                        dialog.destroy()
                        
                        # Recheck service status
                        self._check_all_services()
                    else:
                        messagebox.showerror(API_KEY_DIALOG["set_failed"], data.get("error", "Unknown error"))
                else:
                    data = response.json()
                    messagebox.showerror(API_KEY_DIALOG["set_failed"], data.get("error", f"HTTP {response.status_code}"))
                    
            except requests.exceptions.Timeout:
                messagebox.showerror(MESSAGES["timeout"], MESSAGES["request_timeout"])
            except requests.exceptions.ConnectionError:
                messagebox.showerror(MESSAGES["connection_failed"], MESSAGES["cannot_connect"])
            except Exception as e:
                messagebox.showerror(MESSAGES["error"], MESSAGES["error_occurred"].format(error=str(e)))
        
        confirm_btn = tk.Button(
            button_frame,
            text=BUTTONS["confirm_and_set"],
            command=set_api_key,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configure text tag colors
        result_text.tag_config("success", foreground=self.success_color)
        result_text.tag_config("error", foreground=self.error_color)
        result_text.tag_config("warning", foreground="#FF9800")
    
    def _show_model_select_dialog(self):
        """Show model selection dialog (simplified version)"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(MODEL_SELECTION["title"])
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=MODEL_SELECTION["title"],
            font=("Arial", 16, "bold"),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 15))
        
        # Instruction text
        info_label = tk.Label(
            main_frame,
            text=MODEL_SELECTION["subtitle"],
            font=("Arial", 10),
            fg="#858585",
            bg=self.bg_color
        )
        info_label.pack(pady=(0, 20))
        
        # Detect service status
        local_ok = self._check_service("http://localhost:5000/health")
        online_ok = self._check_service("http://localhost:5001/health")
        
        # Service selection variable
        self.selected_service_var = tk.StringVar(value=self.server_url)
        
        # Local model option
        local_frame = tk.Frame(main_frame, bg="#2d2d2d", relief=tk.FLAT)
        local_frame.pack(fill=tk.X, pady=10)
        
        local_radio = tk.Radiobutton(
            local_frame,
            text="",
            variable=self.selected_service_var,
            value="http://localhost:5000",
            bg="#2d2d2d",
            activebackground="#2d2d2d",
            selectcolor="#2d2d2d",
            state="normal" if local_ok else "disabled"
        )
        local_radio.pack(side=tk.LEFT, padx=10, pady=15)
        
        local_info_frame = tk.Frame(local_frame, bg="#2d2d2d")
        local_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        status_symbol = "🟢" if local_ok else "🔴"
        local_title = tk.Label(
            local_info_frame,
            text=f"{status_symbol} {MODEL_SELECTION['local_title']}",
            font=("Arial", 12, "bold"),
            fg=self.success_color if local_ok else self.error_color,
            bg="#2d2d2d"
        )
        local_title.pack(anchor=tk.W)
        
        local_desc_text = MODEL_SELECTION['local_running'] if local_ok else MODEL_SELECTION['local_not_running']
        local_desc = tk.Label(
            local_info_frame,
            text=local_desc_text,
            font=("Arial", 9),
            fg="#b0b0b0" if local_ok else "#666666",
            bg="#2d2d2d",
            justify=tk.LEFT
        )
        local_desc.pack(anchor=tk.W, pady=(5, 0))
        
        # Online API option
        online_frame = tk.Frame(main_frame, bg="#2d2d2d", relief=tk.FLAT)
        online_frame.pack(fill=tk.X, pady=10)
        
        online_radio = tk.Radiobutton(
            online_frame,
            text="",
            variable=self.selected_service_var,
            value="http://localhost:5001",
            bg="#2d2d2d",
            activebackground="#2d2d2d",
            selectcolor="#2d2d2d",
            state="normal" if online_ok else "disabled"
        )
        online_radio.pack(side=tk.LEFT, padx=10, pady=15)
        
        online_info_frame = tk.Frame(online_frame, bg="#2d2d2d")
        online_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)
        
        status_symbol = "🟢" if online_ok else "🔴"
        online_title = tk.Label(
            online_info_frame,
            text=f"{status_symbol} {MODEL_SELECTION['online_title']}",
            font=("Arial", 12, "bold"),
            fg=self.success_color if online_ok else self.error_color,
            bg="#2d2d2d"
        )
        online_title.pack(anchor=tk.W)
        
        online_desc_text = MODEL_SELECTION['online_running'] if online_ok else MODEL_SELECTION['online_not_running']
        online_desc = tk.Label(
            online_info_frame,
            text=online_desc_text,
            font=("Arial", 9),
            fg="#b0b0b0" if online_ok else "#666666",
            bg="#2d2d2d",
            justify=tk.LEFT
        )
        online_desc.pack(anchor=tk.W, pady=(5, 0))
        
        # Warning message
        if not local_ok and not online_ok:
            warning_label = tk.Label(
                main_frame,
                text=MODEL_SELECTION["no_service_warning"],
                font=("Arial", 10),
                fg=self.error_color,
                bg=self.bg_color
            )
            warning_label.pack(pady=(10, 0))
        
        # Button area
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text=BUTTONS["cancel"],
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
        
        # Confirm button
        def confirm_selection():
            selected_url = self.selected_service_var.get()
            if selected_url:
                self.server_url = selected_url
                dialog.destroy()
                self._check_all_services()
                
                # Display switch success message
                service_name = "Local Model" if "5000" in selected_url else "Online API"
                self._display_system_message(MODEL_SELECTION["switch_success"].format(
                    service_name=service_name,
                    url=selected_url
                ))
            else:
                messagebox.showwarning(MESSAGES["no_selection"], MESSAGES["select_service"])
        
        confirm_btn = tk.Button(
            button_frame,
            text=BUTTONS["confirm"],
            command=confirm_selection,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)
    
    def _check_service(self, url):
        """Check single service status"""
        try:
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
        
    def _show_memory_dialog(self):
        """Show memory management dialog"""
        if not self.memory_enabled:
            messagebox.showwarning(
                MEMORY_DIALOG["memory_not_enabled"],
                MEMORY_DIALOG["memory_not_enabled_msg"]
            )
            return
            
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(MEMORY_DIALOG["title"])
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=MEMORY_DIALOG["title"],
            font=("Arial", 16, "bold"),
            fg=self.memory_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Create Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Configure style
        style = ttk.Style()
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color)
        
        # Tab 1: Store Memory
        store_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(store_frame, text=MEMORY_DIALOG["store_tab"])
        
        store_label = tk.Label(
            store_frame,
            text=MEMORY_DIALOG["store_label"],
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
            text=BUTTONS["store"],
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
        
        # Tab 2: Recall Memory
        recall_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(recall_frame, text=MEMORY_DIALOG["recall_tab"])
        
        recall_label = tk.Label(
            recall_frame,
            text=MEMORY_DIALOG["recall_label"],
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
            text=MEMORY_DIALOG["recall_button"],
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
        
        # Tab 3: Memory Stats
        stats_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(stats_frame, text=MEMORY_DIALOG["stats_tab"])
        
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
            text=BUTTONS["refresh_stats"],
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
        
        # Initialize stats
        self._refresh_memory_stats()
        
    def _store_memory(self):
        """Store memory"""
        memory_text = self.memory_input.get("1.0", tk.END).strip()
        
        if not memory_text:
            messagebox.showwarning(MESSAGES["empty_input"], MESSAGES["enter_memory"])
            return
            
        try:
            response = requests.post(
                f"{self.memory_url}/store",
                params={"text": memory_text},
                timeout=5
            )
            
            if response.status_code == 200:
                messagebox.showinfo(MEMORY_DIALOG["store_success"], MEMORY_DIALOG["store_success_msg"])
                self.memory_input.delete("1.0", tk.END)
            else:
                messagebox.showerror(MESSAGES["error"], f"Storage failed: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror(MESSAGES["error"], f"Storage exception: {str(e)}")
            
    def _recall_memory(self):
        """Recall memory"""
        query = self.memory_query.get().strip()
        
        if not query:
            messagebox.showwarning(MESSAGES["empty_input"], MESSAGES["enter_keywords"])
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
                    self.memory_results.insert(tk.END, MEMORY_DIALOG["matches_found"].format(count=len(matches)))
                    
                    for i, match in enumerate(matches, 1):
                        text = match.get('text', 'N/A')
                        similarity = match.get('similarity', 0)
                        self.memory_results.insert(
                            tk.END,
                            MEMORY_DIALOG["match_item"].format(index=i, similarity=similarity, text=text)
                        )
                else:
                    self.memory_results.insert(tk.END, MEMORY_DIALOG["no_matches"])
            else:
                messagebox.showerror(MESSAGES["error"], f"Recall failed: {response.status_code}")
                
        except Exception as e:
            messagebox.showerror(MESSAGES["error"], f"Recall exception: {str(e)}")
            
    def _refresh_memory_stats(self):
        """Refresh memory statistics"""
        self.memory_stats.delete("1.0", tk.END)
        
        stats_text = MEMORY_DIALOG["stats_title"]
        stats_text += MEMORY_DIALOG["stats_url"].format(url=self.memory_url)
        stats_text += MEMORY_DIALOG["stats_status"].format(
            status="Enabled" if self.memory_enabled else "Not enabled"
        )
        stats_text += MEMORY_DIALOG["stats_endpoints"]
        stats_text += MEMORY_DIALOG["stats_docs"].format(url=self.memory_url)
        stats_text += MEMORY_DIALOG["stats_features"]
        
        self.memory_stats.insert(tk.END, stats_text)
        
    def _send_message(self):
        """Send message"""
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message:
            return
            
        # Clear input box
        self.input_text.delete("1.0", tk.END)
        
        # Display user message
        self._display_message(STATUS["user_prefix"], message, "user")
        
        # Send request in background thread
        threading.Thread(
            target=self._send_request_thread,
            args=(message,),
            daemon=True
        ).start()
        
    def _send_request_thread(self, message):
        """Thread for sending request"""
        try:
            # If memory is enabled, retrieve relevant memories first
            memory_context = ""
            if self.memory_enabled:
                try:
                    response = requests.get(
                        f"{self.memory_url}/recall",
                        params={"query": message},
                        timeout=30  # Longer timeout for embedding model
                    )
                    if response.status_code == 200:
                        data = response.json()
                        matches = data.get("matches", [])
                        if matches:
                            memory_texts = [m.get('text', '') for m in matches[:3]]
                            memory_context = CHAT["relevant_memory"].format(
                                memories="; ".join(memory_texts)
                            )
                            self.root.after(0, self._display_memory_context, memory_context)
                            self.root.after(0, self._display_system_message, f"🧠 Found {len(matches)} relevant memories")
                except Exception as e:
                    self.root.after(0, self._display_system_message, f"⚠️ Memory recall error: {str(e)}")
            
            # Send to API server
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
                assistant_message = data.get('response', 'No response')
                
                # Display assistant message
                self.root.after(0, self._display_message, STATUS["assistant_prefix"], assistant_message, "assistant")
                
                # Store to memory
                if self.memory_enabled:
                    try:
                        mem_response = requests.post(
                            f"{self.memory_url}/store",
                            params={"text": f"Q:{message} A:{assistant_message}"},
                            timeout=30  # Longer timeout for embedding model
                        )
                        if mem_response.status_code == 200:
                            self.root.after(0, self._display_system_message, "💾 Conversation saved to memory")
                        else:
                            self.root.after(0, self._display_system_message, f"⚠️ Failed to save memory (Status {mem_response.status_code})")
                    except Exception as e:
                        self.root.after(0, self._display_system_message, f"⚠️ Memory storage error: {str(e)}")
            else:
                error_msg = CHAT["request_failed"].format(status_code=response.status_code)
                self.root.after(0, self._display_system_message, error_msg)
                
        except requests.exceptions.Timeout:
            self.root.after(0, self._display_system_message, CHAT["request_timeout"])
        except requests.exceptions.ConnectionError:
            self.root.after(0, self._display_system_message, CHAT["no_server"])
        except Exception as e:
            self.root.after(0, self._display_system_message, MESSAGES["error_occurred"].format(error=str(e)))
            
    def _display_message(self, sender, message, tag):
        """Display message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{sender}:\n", tag)
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.see(tk.END)
        
    def _display_system_message(self, message):
        """Display system message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{STATUS['system_prefix']}{message}\n", "system")
        self.chat_display.see(tk.END)
        
    def _display_memory_context(self, context):
        """Display memory context"""
        self.chat_display.insert(tk.END, f"{context}\n", "memory")
        self.chat_display.see(tk.END)
        
    def _clear_chat(self):
        """Clear chat"""
        self.chat_display.delete("1.0", tk.END)
        self._display_welcome_message()
        
    def run(self):
        """Run UI"""
        self.root.mainloop()


def main():
    """Main function"""
    print("[INFO] Starting Advanced Floating UI...")
    print("[INFO] Features: API Switch + Memory Management")
    
    app = AdvancedFloatingChatUI()
    app.run()


if __name__ == "__main__":
    main()
