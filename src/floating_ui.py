#!/usr/bin/env python3
"""
Floating UI for Gemma Model Client
A modern ChatGPT-like interface with markdown rendering.

Usage:
    python src/floating_ui.py

Requires the model server to be running first!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, font
import requests
import threading
import json
import re
import sys
from typing import Optional

class MarkdownRenderer:
    """Simple markdown renderer for Text widget."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._configure_tags()
    
    def _configure_tags(self, font_size=11):
        """Configure text tags for markdown styling with dark theme."""
        # Fonts with configurable size
        default_font = font.nametofont("TkDefaultFont")
        bold_font = font.Font(family=default_font.cget("family"), size=font_size, weight="bold")
        italic_font = font.Font(family=default_font.cget("family"), size=font_size, slant="italic")
        code_font = font.Font(family="Consolas", size=font_size-1)
        heading_font = font.Font(family=default_font.cget("family"), size=font_size+4, weight="bold")
        
        # Configure tags for dark theme
        self.text_widget.tag_configure("bold", font=bold_font)
        self.text_widget.tag_configure("italic", font=italic_font)
        self.text_widget.tag_configure("code", font=code_font, background="#3c3c3c", foreground="#f48771")
        self.text_widget.tag_configure("code_block", font=code_font, background="#2d2d2d", foreground="#d4d4d4")
        self.text_widget.tag_configure("heading", font=heading_font, foreground="#4ec9b0")
        self.text_widget.tag_configure("link", foreground="#569cd6", underline=True)
        self.text_widget.tag_configure("quote", foreground="#858585", lmargin1=20, lmargin2=20)
        self.text_widget.tag_configure("list_item", lmargin1=20, lmargin2=20)
    
    def render(self, markdown_text: str):
        """Render markdown text in the widget."""
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block_lines = []
        
        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code_text = '\n'.join(code_block_lines) + '\n'
                    self.text_widget.insert(tk.END, code_text, "code_block")
                    code_block_lines = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                continue
            
            if in_code_block:
                code_block_lines.append(line)
                continue
            
            # Headings
            if line.startswith('# '):
                self.text_widget.insert(tk.END, line[2:] + '\n', "heading")
                continue
            elif line.startswith('## '):
                self.text_widget.insert(tk.END, line[3:] + '\n', "heading")
                continue
            elif line.startswith('### '):
                self.text_widget.insert(tk.END, line[4:] + '\n', "heading")
                continue
            
            # Quotes
            if line.startswith('> '):
                self.text_widget.insert(tk.END, line[2:] + '\n', "quote")
                continue
            
            # Lists
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                self.text_widget.insert(tk.END, '• ' + line.strip()[2:] + '\n', "list_item")
                continue
            
            # Parse inline markdown
            self._render_inline(line + '\n')
    
    def _render_inline(self, text: str):
        """Render inline markdown (bold, italic, code, links)."""
        current_pos = 0
        
        # Pattern for inline elements
        patterns = [
            (r'\*\*(.+?)\*\*', 'bold'),  # **bold**
            (r'\*(.+?)\*', 'italic'),     # *italic*
            (r'`([^`]+)`', 'code'),       # `code`
            (r'\[([^\]]+)\]\(([^\)]+)\)', 'link'),  # [text](url)
        ]
        
        # Simple approach: find all patterns and their positions
        elements = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, text):
                elements.append((match.start(), match.end(), match.group(0), tag, match))
        
        # Sort by position
        elements.sort(key=lambda x: x[0])
        
        # Insert text with tags
        pos = 0
        for start, end, matched_text, tag, match in elements:
            # Insert text before match
            if pos < start:
                self.text_widget.insert(tk.END, text[pos:start])
            
            # Insert matched text with tag
            if tag == 'link':
                link_text = match.group(1)
                self.text_widget.insert(tk.END, link_text, tag)
            else:
                inner_text = match.group(1)
                self.text_widget.insert(tk.END, inner_text, tag)
            
            pos = end
        
        # Insert remaining text
        if pos < len(text):
            self.text_widget.insert(tk.END, text[pos:])


class FloatingChatUI:
    """Floating chat window for Gemma model client."""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        self.server_url = server_url
        self.conversation_history = []
        self.always_on_top = False
        self.font_size = 11  # Default font size
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Gemma Chat")
        self.root.geometry("800x600")
        
        # Make window resizable and set minimum size
        self.root.minsize(600, 400)
        
        # Dark theme color scheme with acrylic effect
        self.bg_color = "#1f1e33"  # Dark background
        self.secondary_bg = "#2d2d2d"  # Slightly lighter dark
        self.accent_color = "#0078d4"  # Modern blue accent
        self.text_color = "#e0e0e0"  # Light text
        self.user_msg_bg = "#2b5278"  # Dark blue for user messages
        self.assistant_msg_bg = "#2d2d2d"  # Dark grey for assistant
        self.border_color = "#3f3f3f"  # Subtle borders
        
        self.root.configure(bg=self.bg_color)
        
        # Try to enable acrylic/transparency effect (Windows 11)
        try:
            self.root.attributes('-alpha', 0.50)  # Slight transparency
        except:
            pass
        
        # Check server connection
        if not self._check_server():
            self._show_connection_error()
            return
        
        self._create_ui()
        
    def _check_server(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _show_connection_error(self):
        """Show connection error and exit."""
        error_label = tk.Label(
            self.root,
            text="❌ Cannot connect to model server!\n\nPlease start the server first:\npython src/model_server.py",
            font=("Arial", 12),
            fg="red",
            bg=self.bg_color,
            pady=50
        )
        error_label.pack(expand=True)
        
    def _create_ui(self):
        """Create the UI components."""
        # Top bar with title and controls
        top_frame = tk.Frame(self.root, bg=self.accent_color, height=50)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame,
            text="🤖 Gemma Chat",
            font=("Arial", 14, "bold"),
            fg="white",
            bg=self.accent_color,
            pady=10
        )
        title_label.pack(side=tk.LEFT, padx=15)
        
        # Font size controls
        tk.Label(
            top_frame,
            text="A",
            font=("Arial", 8),
            fg="white",
            bg=self.accent_color
        ).pack(side=tk.RIGHT, padx=2)
        
        font_minus_btn = tk.Button(
            top_frame,
            text="-",
            command=self._decrease_font,
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            width=2,
            cursor="hand2"
        )
        font_minus_btn.pack(side=tk.RIGHT, padx=2)
        
        font_plus_btn = tk.Button(
            top_frame,
            text="+",
            command=self._increase_font,
            bg="#2d2d2d",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            width=2,
            cursor="hand2"
        )
        font_plus_btn.pack(side=tk.RIGHT, padx=2)
        
        tk.Label(
            top_frame,
            text="A",
            font=("Arial", 12),
            fg="white",
            bg=self.accent_color
        ).pack(side=tk.RIGHT, padx=2)
        
        # Pin button (always on top)
        self.pin_btn = tk.Button(
            top_frame,
            text="Pin",
            command=self._toggle_always_on_top,
            bg="#2d2d2d",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            cursor="hand2"
        )
        self.pin_btn.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(
            top_frame,
            text="Clear",
            command=self._clear_history,
            bg="#2d2d2d",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Stats button
        stats_btn = tk.Button(
            top_frame,
            text="Stats",
            command=self._show_stats,
            bg="#2d2d2d",
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            cursor="hand2"
        )
        stats_btn.pack(side=tk.RIGHT, padx=5)
        
        # Chat display area
        chat_frame = tk.Frame(self.root, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrolled text for chat with dark theme
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", self.font_size),
            bg=self.bg_color,
            fg=self.text_color,
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=0,
            insertbackground=self.text_color,  # Cursor color
            selectbackground="#264f78",  # Selection color
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for messages with dark theme
        self.chat_display.tag_configure("user", background=self.user_msg_bg, spacing1=5, spacing3=5, lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_configure("assistant", background=self.assistant_msg_bg, spacing1=5, spacing3=5, lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_display.tag_configure("system", foreground="#858585", font=("Segoe UI", self.font_size-2, "italic"))
        
        # Initialize markdown renderer
        self.md_renderer = MarkdownRenderer(self.chat_display)
        
        # Input area
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        # Text input with dark theme
        self.input_text = tk.Text(
            input_frame,
            height=3,
            font=("Segoe UI", self.font_size),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1,
            bg=self.secondary_bg,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground="#264f78",
            highlightthickness=0,
            padx=10,
            pady=10
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.input_text.bind("<Return>", self._handle_enter)
        self.input_text.bind("<Shift-Return>", lambda e: None)  # Allow Shift+Enter for newline
        self.input_text.focus()
        
        # Send button with dark theme
        send_btn = tk.Button(
            input_frame,
            text="Send →",
            command=self._send_message,
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground="#005a9e",
            activeforeground="white"
        )
        send_btn.pack(side=tk.RIGHT)
        
        # Status bar with dark theme
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Segoe UI", 9),
            fg="#858585",
            bg=self.secondary_bg,
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Welcome message
        self._display_system_message("Welcome! Type your message and press Enter or click Send.")
    
    def _handle_enter(self, event):
        """Handle Enter key press."""
        if not event.state & 0x1:  # Check if Shift is not pressed
            self._send_message()
            return "break"  # Prevent newline
        return None  # Allow Shift+Enter for newline
    
    def _send_message(self):
        """Send message to the model."""
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        
        # Display user message
        self._display_user_message(message)
        
        # Update status
        self._update_status("Generating response...")
        
        # Send request in background thread
        thread = threading.Thread(target=self._generate_response, args=(message,))
        thread.daemon = True
        thread.start()
    
    def _generate_response(self, prompt: str):
        """Generate response from the model with streaming (runs in background thread)."""
        try:
            payload = {
                "prompt": prompt,
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
            
            # Initialize assistant message display
            self.root.after(0, self._start_assistant_message)
            
            # Use streaming endpoint for real-time token display
            response = requests.post(
                f"{self.server_url}/generate_stream",
                json=payload,
                timeout=300,
                stream=True
            )
            
            if response.status_code == 200:
                # Process Server-Sent Events
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data = json.loads(line_str[6:])
                            
                            if 'error' in data:
                                self.root.after(0, self._display_system_message, f"Error: {data['error']}")
                                self.root.after(0, self._update_status, "Error")
                                break
                            
                            token = data.get('token', '')
                            is_done = data.get('done', False)
                            
                            if token:
                                # Display token immediately
                                self.root.after(0, self._append_assistant_token, token)
                            
                            if is_done:
                                # Finish the message
                                self.root.after(0, self._finish_assistant_message)
                                self.root.after(0, self._update_status, "Ready")
                                break
            else:
                self.root.after(0, self._display_system_message, f"Error: {response.status_code}")
                self.root.after(0, self._update_status, "Error")
                
        except Exception as e:
            self.root.after(0, self._display_system_message, f"Error: {str(e)}")
            self.root.after(0, self._update_status, "Error")
    
    def _display_user_message(self, message: str):
        """Display user message in chat."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.insert(tk.END, "You\n", "system")
        self.chat_display.insert(tk.END, f"{message}\n", "user")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _start_assistant_message(self):
        """Start displaying an assistant message (for streaming)."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.insert(tk.END, "Assistant\n", "system")
        
        # Store the starting position for later formatting
        self._assistant_msg_start = self.chat_display.index(tk.END)
        self._assistant_msg_text = ""
        
        self.chat_display.configure(state=tk.DISABLED)
    
    def _append_assistant_token(self, token: str):
        """Append a token to the streaming assistant message."""
        self._assistant_msg_text += token
        
        self.chat_display.configure(state=tk.NORMAL)
        
        # Insert token at the end
        self.chat_display.insert(tk.END, token)
        
        # Apply assistant background to the message
        self.chat_display.tag_add("assistant", self._assistant_msg_start, tk.END)
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _finish_assistant_message(self):
        """Finish the streaming assistant message."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.configure(state=tk.DISABLED)
    
    def _display_assistant_message(self, message: str):
        """Display assistant message with markdown rendering (non-streaming)."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.insert(tk.END, "Assistant\n", "system")
        
        # Store the starting position
        start_pos = self.chat_display.index(tk.END)
        
        # Render markdown
        self.md_renderer.render(message)
        
        # Apply assistant background to the whole message
        self.chat_display.tag_add("assistant", start_pos, tk.END)
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _display_system_message(self, message: str):
        """Display system message."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{message}\n", "system")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def _update_status(self, status: str):
        """Update status label."""
        self.status_label.config(text=status)
    
    def _clear_history(self):
        """Clear conversation history."""
        try:
            response = requests.post(f"{self.server_url}/clear_history")
            if response.status_code == 200:
                self.chat_display.configure(state=tk.NORMAL)
                self.chat_display.delete("1.0", tk.END)
                self.chat_display.configure(state=tk.DISABLED)
                self._display_system_message("Conversation history cleared.")
                self._update_status("History cleared")
        except Exception as e:
            self._display_system_message(f"Error clearing history: {str(e)}")
    
    def _show_stats(self):
        """Show conversation statistics."""
        try:
            response = requests.get(f"{self.server_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                stats_text = (
                    f"📊 Statistics:\n"
                    f"  • Total turns: {stats.get('total_turns', 0)}\n"
                    f"  • Tokens generated: {stats.get('total_tokens_generated', 0)}\n"
                    f"  • Sessions: {stats.get('conversation_sessions', 0)}"
                )
                self._display_system_message(stats_text)
        except Exception as e:
            self._display_system_message(f"Error fetching stats: {str(e)}")
    
    def _increase_font(self):
        """Increase font size."""
        if self.font_size < 20:
            self.font_size += 1
            self._apply_font_size()
    
    def _decrease_font(self):
        """Decrease font size."""
        if self.font_size > 8:
            self.font_size -= 1
            self._apply_font_size()
    
    def _apply_font_size(self):
        """Apply font size to all text widgets."""
        # Update chat display
        self.chat_display.configure(font=("Segoe UI", self.font_size))
        
        # Update input text
        self.input_text.configure(font=("Segoe UI", self.font_size))
        
        # Update markdown renderer
        self.md_renderer._configure_tags(self.font_size)
        
        # Update system message tag
        self.chat_display.tag_configure("system", foreground="#858585", font=("Segoe UI", self.font_size-2, "italic"))
        
        self._update_status(f"Font size: {self.font_size}")
    
    def _toggle_always_on_top(self):
        """Toggle always on top mode."""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        
        if self.always_on_top:
            self.pin_btn.config(bg=self.accent_color, fg="white")
            self._update_status("Window pinned (always on top)")
        else:
            self.pin_btn.config(bg="#2d2d2d", fg="white")
            self._update_status("Window unpinned")
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()


def main():
    """Main function."""
    print("🚀 Starting Gemma Chat UI...")
    print("   Make sure model server is running: python src/model_server.py")
    
    app = FloatingChatUI()
    app.run()


if __name__ == "__main__":
    main()

