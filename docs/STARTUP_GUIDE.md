# 🚀 ContextAutoFeedAgent-CAFA 启动指南

## ✅ 问题已解决！

### 🔧 **修复内容**
1. **更新了UI引用** - 将`smart_launcher.py`更新为`smart_launcher_v2.py`
2. **增加了超时时间** - 从5秒增加到10秒，提高连接稳定性
3. **验证了服务器状态** - 两个服务器都运行正常

### 📊 **当前状态**
- ✅ **本地模型服务器** (端口5000): 运行正常
- ✅ **在线API服务器** (端口5001): 运行正常  
- ✅ **UI界面**: 已成功启动

## 🎯 **推荐启动方式**

### 方式1: 使用智能启动器 (推荐)
```bash
python smart_launcher_v2.py
```
或双击 `smart_start_v2.bat`

### 方式2: 使用快速启动器
```bash
python quick_start.py
```
或双击 `quick_start.bat`

### 方式3: 使用一键启动器
```bash
python one_click_start_v2.py
```
或双击 `one_click_start_v2.bat`

## 🔍 **故障排除**

### 如果仍然遇到连接问题：

1. **检查服务器状态**
   ```bash
   python test_connection.py
   ```

2. **手动启动服务器**
   ```bash
   # 启动在线API服务器
   python src/online_model_server.py
   
   # 启动UI界面
   python src/enhanced_floating_ui.py
   ```

3. **检查端口占用**
   ```bash
   netstat -ano | findstr :5000
   netstat -ano | findstr :5001
   ```

## 🎉 **功能验证**

启动成功后，您应该能够：
- ✅ 看到UI界面正常显示
- ✅ 点击"Switch API"按钮切换API服务
- ✅ 在API选择对话框中看到服务器状态
- ✅ 成功连接到选定的API服务

## 📞 **技术支持**

如果仍有问题，请检查：
1. Python环境是否正确安装
2. 必要文件是否存在
3. 防火墙是否阻止了端口访问
4. 是否有其他程序占用了端口

---

**现在您可以正常使用ContextAutoFeedAgent-CAFA了！** 🎉

