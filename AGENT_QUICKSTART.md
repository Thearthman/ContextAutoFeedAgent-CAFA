# Qwen Agent System - Quick Start Guide

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate.fish  # or: source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

New packages added:
- `qwen-agent>=0.0.8` - Agent framework
- `beautifulsoup4>=4.12.0` - Web scraping
- `lxml>=5.0.0` - HTML parsing
- `pillow>=10.0.0` - Image support (Qwen-VL)
- `qwen-vl-utils>=0.0.1` - Qwen utilities

### Step 2: Start the Agent Server

```bash
python src/qwen_agent_server.py
```

**First time?**
- Model will download to `/mnt/g/huggingface` (cache location)
- Loading takes 2-4 minutes
- Uses ~8-10GB VRAM

**What's happening:**
- Loading Qwen2-VL-7B-Instruct with 4-bit quantization
- Registering 3 tools: google_search, read_webpage, read_local_file
- Starting Flask server on port 5001

### Step 3: Launch the UI

```bash
# In a new terminal (keep server running)
python src/agent_ui.py
```

You should see a modern chat window titled "Qwen Agent Chat" 🤖

---

## 💬 Try These Examples

### Example 1: Web Search
```
You: What's the latest news on quantum computing?
```
**What happens:**
1. Agent thinks "I need current information"
2. 🔍 Calls `google_search("quantum computing news 2025")`
3. Gets top 10 search results
4. 📄 May call `read_webpage(url)` to read an article
5. Synthesizes and responds

### Example 2: File Reading
```
You: Read my README.md file and summarize it
```
**What happens:**
1. Agent calls `read_local_file("README.md")`
2. Reads the file content
3. Summarizes the content

### Example 3: Combined Research
```
You: Search for Python async best practices and read the top article
```
**What happens:**
1. 🔍 `google_search("Python async best practices")`
2. 📄 `read_webpage(top_result_url)`
3. Extracts and summarizes content

---

## 🔧 UI Features

### Tool Details Toggle
Click the **🔧** button to show/hide detailed tool execution:
- **ON** (yellow): See all tool calls, parameters, and results
- **OFF** (gray): Only see final agent response

### Other Buttons
- **📌 Pin**: Keep window always on top
- **🧹 Clear**: Clear conversation history

---

## 🛠️ Available Tools

### 1. google_search(query, num_results=10)
Searches Google and returns results.
- **Returns**: Titles, URLs, snippets
- **Autonomous**: Agent decides when to search
- **Rate limit**: 1 second delay between searches

### 2. read_webpage(url, max_length=5000)
Extracts content from a webpage.
- **Returns**: Clean text without ads/navigation
- **Max content**: 5000 characters (configurable)
- **Works on**: Most websites, may fail on heavy JavaScript sites

### 3. read_local_file(file_path, max_length=10000)
Reads local .md or .txt files.
- **Supported**: `.md` and `.txt` only
- **Security**: Path validation, no directory traversal
- **Max content**: 10000 characters

---

## 📊 How It Works

### Agent Decision Process

```
User Query
    ↓
Agent Reasoning: "Do I need external information?"
    ↓
    ├─ NO → Direct response
    ↓
    └─ YES → Call tool(s)
          ↓
      Tool Execution
          ↓
      Tool Results
          ↓
    Agent Reasoning: "Do I need more info?"
          ↓
          ├─ YES → Call more tools (multi-turn)
          ↓
          └─ NO → Synthesize final response
```

### Streaming Events

The UI shows real-time events via Server-Sent Events (SSE):

1. **🔍 Tool Call**: `{"type": "tool_call", "tool": "google_search", "params": {...}}`
2. **✓ Tool Result**: `{"type": "tool_result", "result": "..."}`
3. **💬 Response**: `{"type": "response", "token": "...", "done": false}`
4. **✅ Done**: `{"type": "response", "token": "", "done": true}`

---

## 🔍 Troubleshooting

### Server won't start

**Error: Port 5001 already in use**
```bash
# Find and kill process
lsof -i :5001
kill -9 <PID>
```

**Error: qwen-agent not found**
```bash
pip install qwen-agent
```

**Error: Model loading fails**
- Check VRAM: Need ~8-10GB free
- Check disk space: Model is ~5-7GB
- Check internet: First download needs connection

### UI won't connect

**Error: Cannot connect to server**
1. Ensure server is running: `curl http://localhost:5001/health`
2. Check server terminal for errors
3. Restart server if frozen

### Tools not working

**Web search returns errors**
- May be rate-limited by Google
- Try waiting 1-2 minutes
- Consider Google Custom Search API in future

**Webpage reading fails**
- Some sites block scrapers
- JavaScript-heavy sites may not work
- Try different URLs

**File reading fails**
- Check file path is correct
- Only .md and .txt supported
- Ensure file exists and is readable

---

## 🎯 Next Steps

1. **Test the system** with various queries
2. **Upgrade to 30B model** for better quality:
   - Edit `qwen_agent_server.py`
   - Change `MODEL_NAME = "Qwen/Qwen2-VL-30B-Instruct"`
   - Restart server
3. **Add more tools** in `src/tools/`
4. **Integrate with Obsidian** (future)

---

## 📝 API Endpoints

For programmatic access:

```bash
# Health check
curl http://localhost:5001/health

# Generate with tools
curl -X POST http://localhost:5001/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Search for Python tutorials"}'

# Stream response
curl -X POST http://localhost:5001/generate_stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?"}'

# Clear history
curl -X POST http://localhost:5001/clear_history
```

---

## 🔄 Legacy Gemma System

Still available for non-agent use:

```bash
# Start Gemma server (port 5000)
python src/model_server.py

# Use Gemma UI
python src/floating_ui.py
```

No tool support, but may have different response style.

---

## 📞 Need Help?

- Check `MEMORY.md` for technical details
- Check `README.md` for full documentation
- Review server logs for errors
- Test with simple queries first

---

**Built with ❤️ using qwen-agent framework**

