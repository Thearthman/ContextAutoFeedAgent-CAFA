# Obsidian Gemma Plugin - Development Roadmap

**Project**: Obsidian plugin to integrate local Gemma AI assistant  
**Status**: Planning Phase  
**Started**: October 7, 2025

---

## 🎯 Project Goals

Build an Obsidian plugin that:
1. Connects to our existing Gemma model server (localhost:5000)
2. Provides AI chat interface within Obsidian
3. Offers context-aware note assistance
4. Maintains dark theme aesthetic
5. Works seamlessly with personal knowledge management workflow

---

## 📋 Current Infrastructure

### ✅ What We Have
- [x] Gemma-3-12B model with 4-bit quantization
- [x] Model server running on localhost:5000 with streaming support
- [x] Flask API with `/generate` and `/generate_stream` endpoints
- [x] Dark-themed floating UI (standalone Python app)
- [x] Custom StoppingCriteria for proper EOS handling
- [x] Real-time token streaming (no delays!)

### Server Endpoints Available
```
GET  /health              - Check server status
POST /generate            - Generate complete response (blocking)
POST /generate_stream     - Stream tokens via SSE (real-time)
POST /clear_history       - Clear conversation history
GET  /stats              - Get generation statistics
POST /update_system_prompt - Change system prompt
```

---

## 🗺️ Development Phases

### Phase 1: MVP (Week 1) - Basic Plugin
**Goal**: Get a working plugin that can talk to Gemma

#### Tasks
- [ ] **Setup Plugin Structure**
  - [ ] Create plugin folder: `.obsidian/plugins/obsidian-gemma/`
  - [ ] Create manifest.json
  - [ ] Create main.ts (entry point)
  - [ ] Setup TypeScript build config
  - [ ] Add package.json with dependencies

- [ ] **Basic Server Communication**
  - [ ] Implement fetch to localhost:5000/generate
  - [ ] Error handling for server connection
  - [ ] Test with simple prompt

- [ ] **Simple UI Components**
  - [ ] Add ribbon icon (chat bubble)
  - [ ] Create basic modal for chat
  - [ ] Input field + send button
  - [ ] Display response

- [ ] **Essential Commands**
  - [ ] Command: "Ask Gemma" (opens modal)
  - [ ] Command: "Summarize current note"
  - [ ] Command: "Explain selection"

**Deliverable**: Working plugin that can send prompts and receive responses

---

### Phase 2: Chat Interface (Week 2) - Enhanced UX
**Goal**: Proper chat panel with streaming

#### Tasks
- [ ] **Sidebar Chat View**
  - [ ] Register custom view type
  - [ ] Create chat panel in right sidebar
  - [ ] Chat message display (user + assistant)
  - [ ] Auto-scroll to latest message

- [ ] **Streaming Support**
  - [ ] Connect to /generate_stream endpoint
  - [ ] Parse SSE (Server-Sent Events)
  - [ ] Update UI token-by-token
  - [ ] Show "typing" indicator

- [ ] **Context Awareness**
  - [ ] Include current note in context
  - [ ] Show active file name in chat
  - [ ] Add "Use current note" toggle

- [ ] **Dark Theme Styling**
  - [ ] Match Obsidian's dark theme
  - [ ] Use CSS variables for colors
  - [ ] Dark blue for user messages (#2b5278)
  - [ ] Dark grey for assistant (#2d2d2d)
  - [ ] Smooth animations

**Deliverable**: Beautiful chat interface with streaming responses

---

### Phase 3: Note Intelligence (Week 3) - Power Features
**Goal**: Deep Obsidian integration

#### Tasks
- [ ] **Smart Note Commands**
  - [ ] "Generate outline from selection"
  - [ ] "Expand this idea"
  - [ ] "Find related notes"
  - [ ] "Suggest tags for this note"
  - [ ] "Create atomic note from selection"

- [ ] **Vault-Wide Features**
  - [ ] Search vault with natural language
  - [ ] Multi-note synthesis
  - [ ] Daily summary generator
  - [ ] Research assistant (query multiple notes)

- [ ] **Knowledge Graph Integration**
  - [ ] Suggest backlinks
  - [ ] Find connections between notes
  - [ ] Visualize concept relationships

- [ ] **Templates & Automation**
  - [ ] AI-generated note templates
  - [ ] Smart daily note generation
  - [ ] Auto-tagging on save

**Deliverable**: Intelligent note-taking assistant

---

### Phase 4: Advanced Features (Week 4+) - Polish
**Goal**: Production-ready, delightful to use

#### Tasks
- [ ] **Settings Panel**
  - [ ] Configure server URL
  - [ ] Adjust max tokens
  - [ ] Custom system prompts
  - [ ] Enable/disable features
  - [ ] Hotkey customization

- [ ] **Performance Optimization**
  - [ ] Cache responses
  - [ ] Debounce requests
  - [ ] Cancel in-flight requests
  - [ ] Background processing

- [ ] **Error Handling**
  - [ ] Graceful server disconnection
  - [ ] Retry logic
  - [ ] User-friendly error messages
  - [ ] Connection status indicator

- [ ] **Quality of Life**
  - [ ] Code syntax highlighting in responses
  - [ ] Copy response button
  - [ ] Regenerate response
  - [ ] Edit and resend
  - [ ] Export chat history
  - [ ] Conversation branches

**Deliverable**: Polished, production-ready plugin

---

## 📁 Project Structure

```
.obsidian/plugins/obsidian-gemma/
├── manifest.json          # Plugin metadata
├── main.ts               # Entry point
├── src/
│   ├── settings.ts       # Settings tab
│   ├── chatView.ts       # Chat sidebar panel
│   ├── gemmaClient.ts    # API communication
│   ├── commands.ts       # Command definitions
│   └── utils.ts          # Helper functions
├── styles.css            # Dark theme styles
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── rollup.config.js      # Build configuration
```

---

## 🔧 Technical Stack

### Frontend (Plugin)
- **Language**: TypeScript
- **Framework**: Obsidian API
- **Build**: Rollup
- **Styling**: CSS (using Obsidian CSS variables)

### Backend (Existing)
- **Server**: Flask (Python)
- **Model**: Gemma-3-12B (4-bit quantized)
- **Streaming**: Server-Sent Events (SSE)
- **Port**: localhost:5000

---

## 📊 Success Metrics

### Phase 1 (MVP)
- [ ] Plugin loads without errors
- [ ] Can send prompt and receive response
- [ ] Commands appear in command palette
- [ ] Basic error handling works

### Phase 2 (Chat)
- [ ] Chat panel opens in sidebar
- [ ] Messages display correctly
- [ ] Streaming shows tokens in real-time
- [ ] UI is responsive and smooth

### Phase 3 (Intelligence)
- [ ] Context-aware responses
- [ ] Vault search works accurately
- [ ] Commands enhance note-taking workflow
- [ ] No performance issues with large vaults

### Phase 4 (Polish)
- [ ] Settings persist correctly
- [ ] No crashes or errors
- [ ] Fast response times
- [ ] Delightful user experience

---

## 🐛 Known Challenges & Solutions

### Challenge 1: CORS Issues
**Problem**: Browser may block localhost requests  
**Solution**: 
```python
# Add to model_server.py
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})
```

### Challenge 2: SSE in TypeScript
**Problem**: Parsing Server-Sent Events  
**Solution**: Use EventSource or fetch with ReadableStream

### Challenge 3: Context Size
**Problem**: Large notes exceed token limit  
**Solution**: Implement smart truncation/summarization

### Challenge 4: Obsidian API Learning Curve
**Problem**: Complex API  
**Solution**: Study sample plugins, use TypeScript types

---

## 📚 Resources

### Obsidian Plugin Development
- [Obsidian API Docs](https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin)
- [Sample Plugin](https://github.com/obsidianmd/obsidian-sample-plugin)
- [Community Plugins](https://github.com/obsidianmd/obsidian-releases)

### Similar Plugins (for inspiration)
- Text Generator Plugin (OpenAI integration)
- Copilot Plugin
- Smart Connections (semantic search)

### Our Codebase
- `src/model_server.py` - API endpoints
- `src/main.py` - Model interface with StopOnTokens
- `src/floating_ui.py` - UI reference (dark theme, streaming)

---

## 🎨 Design Principles

1. **Non-intrusive**: Should enhance, not disrupt workflow
2. **Fast**: Responses should feel instant
3. **Contextual**: Always aware of current note
4. **Private**: Everything stays local (no cloud)
5. **Beautiful**: Match Obsidian's aesthetic
6. **Reliable**: Graceful degradation if server down

---

## 🚀 Getting Started

### Prerequisites
```bash
# Node.js and npm
node --version  # Should be v16+
npm --version

# Obsidian installed
# Vault created and accessible
```

### Development Setup
```bash
# 1. Create plugin folder
mkdir -p "VAULT_PATH/.obsidian/plugins/obsidian-gemma"
cd "VAULT_PATH/.obsidian/plugins/obsidian-gemma"

# 2. Initialize npm project
npm init -y

# 3. Install dependencies
npm install --save-dev typescript @types/node
npm install --save-dev @rollup/plugin-typescript rollup
npm install --save-dev obsidian

# 4. Create TypeScript config
# (we'll do this in next steps)

# 5. Enable developer mode in Obsidian
# Settings > Community Plugins > Turn on restricted mode > Developer mode
```

---

## 📝 Next Steps

**Immediate Actions**:
1. ✅ Create this working document
2. [ ] Setup plugin folder structure
3. [ ] Create manifest.json
4. [ ] Initialize TypeScript project
5. [ ] Build "Hello World" plugin
6. [ ] Test loading in Obsidian

**This Week's Goal**: Phase 1 MVP completed

---

## 📅 Timeline

| Week | Phase | Deliverable | Status |
|------|-------|-------------|--------|
| 1 | MVP | Working plugin with basic commands | 🔄 Planning |
| 2 | Chat UI | Streaming chat interface | ⏳ Not started |
| 3 | Intelligence | Context-aware features | ⏳ Not started |
| 4+ | Polish | Production-ready plugin | ⏳ Not started |

---

## 💭 Notes & Ideas

### Future Enhancements (Beyond v1.0)
- Image understanding (if switching to Gemini Pro)
- Collaborative features (share prompts)
- Plugin marketplace for prompt templates
- Integration with other Obsidian plugins (Dataview, Templater)

### Community Features
- Could open-source after v1.0
- Share with Obsidian community
- Support for other local LLMs (Llama, Mistral)

---

**Last Updated**: October 7, 2025  
**Next Review**: After Phase 1 completion

