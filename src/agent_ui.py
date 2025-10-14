#!/usr/bin/env python3
"""
Agent UI for Qwen Agent Server
A ChatGPT-like interface with real-time tool usage display.

Usage:
    python src/agent_ui.py

Requires the qwen_agent_server to be running first!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font
import requests
import threading
import json
import re
import sys
from typing import Optional
import urllib3.exceptions

class MarkdownRenderer:
    """Simple markdown renderer for Text widget."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._configure_tags()
    
    def _configure_tags(self, font_size=11):
        """Configure text tags for markdown styling with dark theme."""
        default_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(family=default_font.cget("family"), size=font_size, weight="bold")
        italic_font = font.Font(family=default_font.cget("family"), size=font_size, slant="italic")
        code_font = font.Font(family="Consolas", size=font_size-1)
        heading_font = font.Font(family=default_font.cget("family"), size=font_size+4, weight="bold")
        
        self.text_widget.tag_configure("bold", font=bold_font)
        self.text_widget.tag_configure("italic", font=italic_font)
        self.text_widget.tag_configure("code", font=code_font, background="#3c3c3c", foreground="#f48771")
        self.text_widget.tag_configure("code_block", font=code_font, background="#2d2d2d", foreground="#d4d4d4")
        self.text_widget.tag_configure("heading", font=heading_font, foreground="#4ec9b0")
        self.text_widget.tag_configure("link", foreground="#569cd6", underline=True)
        self.text_widget.tag_configure("quote", foreground="#858585", lmargin1=20, lmargin2=20)
        self.text_widget.tag_configure("list_item", lmargin1=20, lmargin2=20)
        # Tool-specific tags
        self.text_widget.tag_configure("tool_call", foreground="#ffd700", font=bold_font)
        self.text_widget.tag_configure("tool_result", foreground="#90ee90", background="#2d2d2d", lmargin1=20, lmargin2=20)
        self.text_widget.tag_configure("thinking", foreground="#a0a0a0", font=italic_font)
    
    def render(self, markdown_text: str):
        """Render markdown text in the widget."""
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    code_text = '\n'.join(code_block_lines) + '\n'
                    self.text_widget.insert(tk.END, code_text, "code_block")
                    code_block_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block_lines.append(line)
                continue
            
            if line.startswith('# '):
                self.text_widget.insert(tk.END, line[2:] + '\n', "heading")
                continue
            elif line.startswith('## '):
                self.text_widget.insert(tk.END, line[3:] + '\n', "heading")
                continue
            elif line.startswith('### '):
                self.text_widget.insert(tk.END, line[4:] + '\n', "heading")
                continue
            
            if line.startswith('> '):
                self.text_widget.insert(tk.END, line[2:] + '\n', "quote")
                continue
            
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                self.text_widget.insert(tk.END, '• ' + line.strip()[2:] + '\n', "list_item")
                continue
            
            self._render_inline(line + '\n')
    
    def _render_inline(self, text: str):
        """Render inline markdown (bold, italic, code, links)."""
        patterns = [
            (r'\*\*(.+?)\*\*', 'bold'),
            (r'\*(.+?)\*', 'italic'),
            (r'`([^`]+)`', 'code'),
            (r'\[([^\]]+)\]\(([^\)]+)\)', 'link'),
        ]
        
        elements = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, text):
                elements.append((match.start(), match.end(), match.group(0), tag, match))
        
        elements.sort(key=lambda x: x[0])
        
        pos = 0
        for start, end, matched_text, tag, match in elements:
            if pos < start:
                self.text_widget.insert(tk.END, text[pos:start])
            
            if tag == 'link':
                link_text = match.group(1)
                self.text_widget.insert(tk.END, link_text, tag)
            else:
                inner_text = match.group(1)
                self.text_widget.insert(tk.END, inner_text, tag)
            
            pos = end
        
        if pos < len(text):
            self.text_widget.insert(tk.END, text[pos:])


class AgentChatUI:
    """Floating chat window for Qwen Agent with tool usage display."""
    
    def __init__(self, server_url: str = "http://localhost:5001"):
        self.server_url = server_url
        self.conversation_history = []
        self.always_on_top = False
        self.font_size = 11
        self.show_tool_details = True
        
        self.root = tk.Tk()
        self.root.title("Qwen Agent Chat")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Dark theme
        self.bg_color = "#1f1e33"
        self.secondary_bg = "#2d2d2d"
        self.accent_color = "#0078d4"
        self.text_color = "#e0e0e0"
        self.user_msg_bg = "#2b5278"
        self.assistant_msg_bg = "#2d2d2d"
        self.border_color = "#3f3f3f"
        
        self.root.configure(bg=self.bg_color)
        
        try:
            self.root.attributes('-alpha', 0.95)
        except:
            pass
        
        if not self._check_server():
            self._show_connection_error()
            return
        
        self._create_ui()
    
    def _check_server(self) -> bool:
        """Check if agent server is running."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _show_connection_error(self):
        """Show connection error."""
        error_label = tk.Label(
            self.root,
            text="❌ Cannot connect to Qwen Agent Server!\n\nStart server: python src/qwen_agent_server.py",
            font=("Arial", 12),
            fg="red",
            bg=self.bg_color,
            pady=50
        )
        error_label.pack(expand=True)
    
    def _create_ui(self):
        """Create UI components."""
        # Top bar with controls
        top_bar = tk.Frame(self.root, bg=self.secondary_bg, height=40)
        top_bar.pack(fill=tk.X, padx=0, pady=0)
        top_bar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            top_bar,
            text="🤖 Qwen Agent",
            font=("Arial", 11, "bold"),
            fg=self.text_color,
            bg=self.secondary_bg
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Pin button
        self.pin_button = tk.Button(
            top_bar,
            text="📌",
            command=self._toggle_pin,
            bg=self.secondary_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            font=("Arial", 12),
            cursor="hand2"
        )
        self.pin_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        clear_button = tk.Button(
            top_bar,
            text="🧹",
            command=self._clear_history,
            bg=self.secondary_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            font=("Arial", 12),
            cursor="hand2"
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Tool details toggle
        self.tool_toggle_button = tk.Button(
            top_bar,
            text="🔧",
            command=self._toggle_tool_details,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 12),
            cursor="hand2"
        )
        self.tool_toggle_button.pack(side=tk.RIGHT, padx=5)
        
        # Chat display area
        chat_frame = tk.Frame(self.root, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", self.font_size),
            insertbackground=self.text_color,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Initialize markdown renderer
        self.renderer = MarkdownRenderer(self.chat_display)
        
        # Input area
        input_frame = tk.Frame(self.root, bg=self.secondary_bg)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.input_field = tk.Text(
            input_frame,
            height=3,
            bg=self.secondary_bg,
            fg=self.text_color,
            font=("Arial", 10),
            insertbackground=self.text_color,
            relief=tk.FLAT,
            borderwidth=5,
            padx=5,
            pady=5
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind('<Return>', self._on_enter_key)
        self.input_field.bind('<Shift-Return>', self._on_shift_enter)
        
        send_button = tk.Button(
            input_frame,
            text="Send",
            command=self._send_message,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            cursor="hand2"
        )
        send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Welcome message
        self._display_welcome()
    
    def _display_welcome(self):
        """Display welcome message."""
        welcome = """# Welcome to Qwen Agent! 🤖

I'm an AI assistant with access to tools for web search and file reading.

**Available Tools:**
- 🔍 **Web Search**: I can search Google for current information
- 📄 **Web Reader**: I can read and extract content from webpages  
- 📂 **File Reader**: I can read your local .md and .txt files

Just ask me anything, and I'll autonomously use tools when needed!

**Tool Display:** Click 🔧 to toggle detailed tool usage visibility.

---
"""
        self._add_message("assistant", welcome)
    
    def _toggle_pin(self):
        """Toggle always on top."""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        self.pin_button.config(
            bg=self.accent_color if self.always_on_top else self.secondary_bg,
            fg="white" if self.always_on_top else self.text_color
        )
    
    def _toggle_tool_details(self):
        """Toggle tool details visibility."""
        self.show_tool_details = not self.show_tool_details
        self.tool_toggle_button.config(
            bg=self.accent_color if self.show_tool_details else self.secondary_bg,
            fg="white" if self.show_tool_details else self.text_color
        )
    
    def _clear_history(self):
        """Clear conversation history."""
        try:
            requests.post(f"{self.server_url}/clear_history")
            self.conversation_history = []
            self.chat_display.delete(1.0, tk.END)
            self._display_welcome()
        except:
            pass
    
    def _on_enter_key(self, event):
        """Handle Enter key."""
        self._send_message()
        return 'break'
    
    def _on_shift_enter(self, event):
        """Handle Shift+Enter (new line)."""
        return None
    
    def _send_message(self):
        """Send message to agent."""
        user_input = self.input_field.get(1.0, tk.END).strip()
        if not user_input:
            return
        
        self.input_field.delete(1.0, tk.END)
        self._add_message("user", user_input)
        
        # Start generation in thread
        thread = threading.Thread(target=self._generate_response, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def _add_message(self, role: str, content: str):
        """Add message to chat display."""
        self.chat_display.insert(tk.END, "\n")
        
        if role == "user":
            self.chat_display.insert(tk.END, "You:\n", "heading")
            self.chat_display.insert(tk.END, content + "\n\n")
        elif role == "assistant":
            self.chat_display.insert(tk.END, "Assistant:\n", "heading")
            self.renderer.render(content)
            self.chat_display.insert(tk.END, "\n")
        
        self.chat_display.see(tk.END)
    
    def _add_tool_call(self, tool_name: str, params: dict):
        """Display tool call."""
        if not self.show_tool_details:
            return
        
        icons = {
            'google_search': '🔍',
            'read_webpage': '📄',
            'read_local_file': '📂'
        }
        icon = icons.get(tool_name, '🔧')
        
        self.chat_display.insert(tk.END, f"\n{icon} Using {tool_name}\n", "tool_call")
        
        # Show params if relevant
        if 'query' in params:
            self.chat_display.insert(tk.END, f"   Query: {params['query']}\n", "thinking")
        elif 'url' in params:
            self.chat_display.insert(tk.END, f"   URL: {params['url']}\n", "thinking")
        elif 'file_path' in params:
            self.chat_display.insert(tk.END, f"   File: {params['file_path']}\n", "thinking")
        
        self.chat_display.see(tk.END)
    
    def _add_tool_result(self, result: str):
        """Display tool result."""
        if not self.show_tool_details:
            return
        
        # Truncate long results
        display_result = result[:200] + "..." if len(result) > 200 else result
        self.chat_display.insert(tk.END, f"   ✓ Result: {display_result}\n\n", "tool_result")
        self.chat_display.see(tk.END)
    
    def _generate_response(self, prompt: str):
        """Generate response with streaming."""
        try:
            url = f"{self.server_url}/generate_stream"
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'prompt': prompt})
            
            response = requests.post(url, headers=headers, data=data, stream=True, timeout=300)
            
            # Start assistant message
            self.root.after(0, lambda: self.chat_display.insert(tk.END, "\nAssistant:\n", "heading"))
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        try:
                            event = json.loads(line[6:])
                            
                            if event.get('type') == 'tool_call':
                                # Tool is being called
                                tool = event.get('tool', 'unknown')
                                params = event.get('params', {})
                                self.root.after(0, lambda t=tool, p=params: self._add_tool_call(t, p))
                            
                            elif event.get('type') == 'tool_result':
                                # Tool returned result
                                result = event.get('result', '')
                                self.root.after(0, lambda r=result: self._add_tool_result(r))
                            
                            elif event.get('type') == 'response':
                                # Agent's response tokens
                                token = event.get('token', '')
                                done = event.get('done', False)
                                
                                if not done and token:
                                    self.root.after(0, lambda t=token: self.chat_display.insert(tk.END, t))
                                    self.root.after(0, lambda: self.chat_display.see(tk.END))
                            
                            elif event.get('type') == 'error':
                                error = event.get('error', 'Unknown error')
                                self.root.after(0, lambda e=error: self.chat_display.insert(tk.END, f"\n❌ Error: {e}\n", "tool_call"))
                        
                        except json.JSONDecodeError:
                            continue
            
            # Add final spacing
            self.root.after(0, lambda: self.chat_display.insert(tk.END, "\n"))
            
        except Exception as e:
            error_msg = f"\n❌ Error: {str(e)}\n"
            self.root.after(0, lambda: self.chat_display.insert(tk.END, error_msg, "tool_call"))
    
    def run(self):
        """Start the UI."""
        self.root.mainloop()


if __name__ == "__main__":
    app = AgentChatUI()
    app.run()

