# ContextAutoFeedAgent-CAFA 一键启动程序

## 📋 启动器说明

本项目提供了多个启动器，满足不同的使用需求：

### 🚀 主要启动器

#### 1. **智能启动器** (`smart_launcher_v2.py`)
- **功能**: 自动检测服务状态，智能选择启动服务
- **特点**: 
  - 自动检测API Key配置
  - 智能选择本地模型或在线API
  - 支持自定义服务选择
  - 实时状态监控
- **使用**: `python smart_launcher_v2.py`

#### 2. **快速启动器** (`quick_start.py`)
- **功能**: 快速启动UI界面
- **特点**:
  - 检查服务器状态
  - 直接启动UI
  - 简单易用
- **使用**: `python quick_start.py`

#### 3. **一键启动器** (`one_click_start_v2.py`)
- **功能**: 整合所有启动选项
- **特点**:
  - 提供多种启动方式
  - 环境检查
  - 用户友好界面
- **使用**: `python one_click_start_v2.py`

### 🖥️ Windows批处理文件

- `smart_start_v2.bat` - 启动智能启动器
- `quick_start.bat` - 启动快速启动器  
- `one_click_start_v2.bat` - 启动一键启动器

## 🎯 使用建议

### 首次使用
1. **推荐**: 使用 `smart_launcher_v2.py` 或双击 `smart_start_v2.bat`
2. 选择 "智能启动" 选项
3. 系统会自动检测并启动合适的服务

### 日常使用
1. **快速启动**: 使用 `quick_start.py` 或双击 `quick_start.bat`
2. **完整功能**: 使用 `smart_launcher_v2.py`

### 开发调试
1. 手动启动服务器: `python src/online_model_server.py`
2. 启动UI: `python src/enhanced_floating_ui.py`

## 🔧 服务说明

### 服务器类型
- **本地模型服务器** (端口5000): 运行本地Gemma模型
- **在线API服务器** (端口5001): 使用OpenAI等在线API
- **内存API服务** (端口5002): 提供内存管理功能
- **浮动UI界面**: 图形用户界面

### API Key配置
启动器会自动检测以下位置的API Key:
- 环境变量: `OPENAI_API_KEY`, `LLM_API_KEY`, `API_KEY`, `OPENAI_KEY`
- 配置文件: `api_config.json`, `.env`, `config.json`

## 📝 使用流程

1. **环境检查**: 启动器自动检查Python环境和必要文件
2. **服务检测**: 检测各服务器运行状态
3. **API Key检测**: 自动检测API Key配置
4. **服务选择**: 根据配置智能选择或手动选择服务
5. **启动服务**: 按顺序启动选定的服务
6. **状态监控**: 实时监控服务状态

## ⚠️ 注意事项

- 确保Python环境正常
- 确保必要文件存在
- 首次使用建议选择"智能启动"
- 按Ctrl+C可以停止所有服务

## 🎉 功能特性

- ✅ 自动环境检查
- ✅ 智能服务检测
- ✅ API Key自动检测
- ✅ 多种启动模式
- ✅ 实时状态监控
- ✅ 用户友好界面
- ✅ 跨平台支持

## 📞 技术支持

如遇问题，请检查:
1. Python环境是否正确安装
2. 必要文件是否存在
3. 端口是否被占用
4. API Key是否正确配置
