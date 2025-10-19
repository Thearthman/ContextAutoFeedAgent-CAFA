# 🚀 一键启动指南

## 快速开始

### Windows用户
双击 `start.bat` 文件即可启动！

### Linux/Mac用户
```bash
./start.sh
```

### Python用户
```bash
python start.py
```

## 📋 启动模式说明

### 1. 模型服务器
- **用途**: 启动HTTP API服务器
- **端口**: 5000
- **特点**: 模型加载一次，保持在GPU内存中
- **适用**: API调用、开发调试

### 2. 浮动UI界面
- **用途**: 启动图形界面
- **特点**: ChatGPT风格的现代化界面
- **要求**: 需要先启动模型服务器
- **适用**: 日常使用、交互式对话

### 3. 内存工具API
- **用途**: 启动内存管理API
- **端口**: 8000
- **特点**: 语义记忆存储和检索
- **适用**: 知识管理、长期记忆

### 4. 独立模式
- **用途**: 直接运行，无需服务器
- **特点**: 每次启动都重新加载模型
- **适用**: 简单测试、一次性使用

### 5. 全部启动
- **用途**: 启动所有服务
- **特点**: 一键启动完整系统
- **适用**: 完整功能体验

### 6. 安装依赖
- **用途**: 安装/更新Python依赖包
- **特点**: 自动检查并安装所需包
- **适用**: 首次使用、环境更新

## 🔧 高级选项

### 命令行参数

```bash
# 直接启动特定模式
python start.py --mode server      # 启动服务器
python start.py --mode ui          # 启动UI
python start.py --mode memory      # 启动内存API
python start.py --mode standalone  # 独立模式
python start.py --mode all         # 全部启动

# 其他选项
python start.py --install          # 安装依赖
python start.py --check            # 检查系统要求
```

### 环境变量

```bash
# 设置模型路径
export HF_HOME=/path/to/huggingface
export TRANSFORMERS_CACHE=/path/to/huggingface

# 设置CUDA设备
export CUDA_VISIBLE_DEVICES=0
```

## 🐛 常见问题

### Q: 启动失败怎么办？
A: 检查以下几点：
1. 确保在项目根目录运行
2. 检查Python版本（需要3.9+）
3. 确保已安装所有依赖
4. 检查端口是否被占用

### Q: 模型加载很慢？
A: 这是正常的：
- 首次加载需要2-6分钟
- 后续启动会快很多
- 建议使用服务器模式

### Q: UI界面打不开？
A: 可能的原因：
1. 未安装tkinter: `sudo apt-get install python3-tk`
2. 服务器未启动
3. 防火墙阻止连接

### Q: 内存不足？
A: 解决方案：
1. 使用4-bit量化模型
2. 减少max_new_tokens参数
3. 关闭其他GPU程序

## 📊 性能优化

### 启动速度优化
- 使用SSD存储模型
- 启用CUDA优化
- 使用虚拟环境

### 运行性能优化
- 使用服务器模式
- 保持模型在GPU内存中
- 合理设置生成参数

### 内存优化
- 定期清理对话历史
- 使用量化模型
- 监控GPU内存使用

## 🎯 使用建议

### 开发调试
1. 启动模型服务器
2. 使用API进行测试
3. 修改代码后重启客户端

### 日常使用
1. 使用"全部启动"模式
2. 通过UI界面交互
3. 利用内存工具保存重要信息

### 生产部署
1. 使用Docker容器
2. 配置负载均衡
3. 监控系统资源

## 📞 获取帮助

- 查看 `README.md` 获取详细文档
- 检查 `SERVER_SETUP.md` 了解服务器配置
- 参考 `MEMORY_TOOL_README.md` 了解内存工具
- 查看 `ONLINE_LLM_GUIDE.md` 了解在线模型使用

---

**🎉 现在就开始使用吧！选择适合您的启动方式，享受AI助手的强大功能！**
