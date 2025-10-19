
# Model Server Setup Guide

## 🎯 Purpose

The model server approach allows you to:
- **Load the model once** and keep it in GPU memory
- **Modify and test client code instantly** without 2-6 minute reload times
- **Send multiple requests** without reloading checkpoints
- **Develop iteratively** with fast feedback loops

## 🚀 Quick Start

### Step 1: Install Flask (if not already installed)

```bash
source venv/bin/activate.fish
pip install flask
```

### Step 2: Start the Model Server

```bash
python src/model_server.py
```

**What happens:**
- Model loads once (2-6 minutes)
- Stays in GPU memory
- HTTP API server starts on `http://localhost:5000`
- Ready to accept requests

**Output:**
```
======================================================================
🚀 Starting Gemma Model Server...
======================================================================
Loading model with 4-bit quantization...
✅ Model loaded successfully in 180.5 seconds
🌐 Server ready to accept requests on http://localhost:5000
======================================================================
```

### Step 3: Use the Client (in a new terminal)

```bash
# New terminal window/tab
source venv/bin/activate.fish
python src/model_client.py
```

**Now you can:**
- Chat normally
- Exit the client (server keeps running)
- Modify `model_client.py` 
- Restart client instantly (no model reload!)

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Generate Response
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is quantum computing?",
    "max_new_tokens": 200,
    "temperature": 0.7
  }'
```

### Clear History
```bash
curl -X POST http://localhost:5000/clear_history
```

### Get Statistics
```bash
curl http://localhost:5000/stats
```

### Update System Prompt
```bash
curl -X POST http://localhost:5000/update_system_prompt \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "You are a helpful coding assistant."}'
```

### Shutdown Server
```bash
curl -X POST http://localhost:5000/shutdown
```

## 🔧 Usage Patterns

### Pattern 1: Interactive Chat
```bash
# Terminal 1: Start server (leave running)
python src/model_server.py

# Terminal 2: Use interactive client
python src/model_client.py
```

### Pattern 2: Quick Testing
Edit the `quick_test()` function in `model_client.py`:

```python
def quick_test():
    client = GemmaClient()
    
    # Modify these prompts for rapid testing
    prompts = [
        "Your test question 1",
        "Your test question 2",
    ]
    
    for prompt in prompts:
        response = client.generate(prompt, max_new_tokens=200)
        print(f"Response: {response}")
```

Then run:
```bash
# In model_client.py, change:
if __name__ == "__main__":
    quick_test()  # Instead of main()
```

```bash
python src/model_client.py  # Runs in seconds!
```

### Pattern 3: Custom Scripts
Create your own test scripts:

```python
# my_test.py
from src.model_client import GemmaClient

client = GemmaClient()

# Test your specific scenario
response = client.generate("Test prompt", max_new_tokens=100)
print(response)
```

## 💡 Benefits

### Before (Traditional Approach):
```bash
python src/main.py          # 2-6 min load time
# Make code change
python src/main.py          # 2-6 min load time again
# Make another change
python src/main.py          # 2-6 min load time again
```

**Total time for 3 tests: 6-18 minutes** 😫

### After (Server Approach):
```bash
python src/model_server.py  # 2-6 min (ONE TIME)
# Make code change
python src/model_client.py  # <1 second
# Make another change  
python src/model_client.py  # <1 second
```

**Total time for 3 tests: 2-6 minutes** 🚀

## 🎮 Client Commands

When running the interactive client:

- **Normal text**: Send as prompt to model
- **`quit`/`exit`/`bye`**: Exit client (server keeps running)
- **`clear`**: Clear conversation history
- **`stats`**: Show conversation statistics
- **`prompt <text>`**: Update system prompt
- **`shutdown`**: Shutdown the model server

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>
```

### Client can't connect
```bash
# Make sure server is running
curl http://localhost:5000/health

# Check firewall settings if needed
```

### Model errors
Check server terminal for error messages. The server logs all requests and errors.

## 🛑 Stopping Everything

```bash
# Option 1: From client
python src/model_client.py
> shutdown
> yes

# Option 2: From server terminal
Ctrl+C

# Option 3: From command line
curl -X POST http://localhost:5000/shutdown
```

## 📊 Performance Notes

- **First load**: 2-6 minutes (one time)
- **Subsequent requests**: Instant client startup
- **Generation time**: Same as normal (no overhead)
- **GPU memory**: Model stays loaded (~16GB for 27B Q4)
- **Multiple clients**: Can connect from multiple terminals

## 🎯 Best Practices

1. **Keep server running** during development sessions
2. **Use `quick_test()` mode** for rapid iteration
3. **Clear history** between unrelated tests
4. **Monitor GPU memory** with `nvidia-smi`
5. **Shutdown properly** to free GPU memory when done

---

**Happy fast iteration! 🚀**

