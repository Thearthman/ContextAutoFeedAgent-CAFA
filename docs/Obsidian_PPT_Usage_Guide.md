# Obsidian Canvas Presentation Setup Guide

## 🎯 如何在Obsidian中使用PPT演示

### 方法1: 使用Slides插件（推荐）

#### 安装步骤：
1. **安装Slides插件**：
   - 打开Obsidian设置 (Ctrl+,)
   - 进入"Community plugins"
   - 搜索"Slides"
   - 安装并启用

2. **使用演示文件**：
   - 打开 `Obsidian_Presentation_Slides.md`
   - 按 `Ctrl+P` 打开命令面板
   - 搜索 "Slides: Start presentation"
   - 开始演示

#### 快捷键：
- `→` 或 `Space`: 下一张幻灯片
- `←`: 上一张幻灯片
- `Esc`: 退出演示模式
- `F`: 全屏模式

---

### 方法2: 使用Canvas功能

#### 创建Canvas演示：
1. **创建新Canvas**：
   - 按 `Ctrl+N` 创建新笔记
   - 选择 "Canvas" 类型

2. **添加幻灯片**：
   - 在Canvas中添加卡片
   - 每个卡片代表一张幻灯片
   - 复制PPT内容到卡片中

3. **演示模式**：
   - 使用Canvas的演示模式
   - 按 `F11` 全屏
   - 使用方向键导航

---

### 方法3: 使用PDF导出

#### 导出为PDF：
1. **安装Pandoc**：
   ```bash
   # Windows
   choco install pandoc
   
   # macOS
   brew install pandoc
   
   # Linux
   sudo apt install pandoc
   ```

2. **导出命令**：
   ```bash
   pandoc Obsidian_Presentation_Slides.md -o presentation.pdf --pdf-engine=wkhtmltopdf
   ```

3. **在Obsidian中查看**：
   - 将PDF文件放入Obsidian库
   - 使用PDF查看器插件查看

---

### 方法4: 使用Reveal.js插件

#### 安装Reveal.js插件：
1. **安装插件**：
   - 搜索 "Reveal.js" 插件
   - 安装并启用

2. **配置演示**：
   - 在PPT文件中添加frontmatter：
   ```yaml
   ---
   reveal:
     theme: white
     transition: slide
   ---
   ```

3. **开始演示**：
   - 按 `Ctrl+P`
   - 搜索 "Reveal.js: Start presentation"

---

## 🎨 自定义样式

### 添加CSS样式：
1. **创建样式文件**：
   - 在Obsidian库中创建 `styles.css`
   - 添加自定义样式

2. **示例样式**：
   ```css
   .slides {
     font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
   }
   
   .slide h1 {
     color: #2c3e50;
     text-align: center;
   }
   
   .slide h2 {
     color: #34495e;
     border-bottom: 2px solid #3498db;
   }
   
   .slide table {
     width: 100%;
     border-collapse: collapse;
   }
   
   .slide th, .slide td {
     border: 1px solid #ddd;
     padding: 8px;
     text-align: left;
   }
   
   .slide th {
     background-color: #f2f2f2;
   }
   ```

---

## 🚀 最佳实践

### 演示准备：
1. **测试环境**：
   - 提前测试所有插件
   - 确保演示文件正常显示
   - 准备备用方案

2. **内容优化**：
   - 使用清晰的标题
   - 添加适当的空白
   - 使用表格和代码块

3. **交互功能**：
   - 添加链接到相关文档
   - 使用Obsidian的内部链接
   - 准备实时演示

### 演示技巧：
1. **导航**：
   - 熟悉快捷键
   - 准备鼠标操作
   - 练习切换速度

2. **内容展示**：
   - 突出关键信息
   - 使用动画效果
   - 保持节奏

3. **互动**：
   - 准备Q&A环节
   - 使用Obsidian的搜索功能
   - 展示相关文档

---

## 📱 移动端支持

### 在手机上使用：
1. **Obsidian Mobile**：
   - 安装Obsidian Mobile应用
   - 同步演示文件
   - 使用触摸导航

2. **Web版本**：
   - 使用Obsidian Publish
   - 创建公开链接
   - 在任何设备上访问

---

## 🔧 故障排除

### 常见问题：
1. **插件不工作**：
   - 检查插件是否启用
   - 重启Obsidian
   - 更新插件版本

2. **样式问题**：
   - 检查CSS文件
   - 清除缓存
   - 重新加载主题

3. **性能问题**：
   - 关闭不必要的插件
   - 减少文件大小
   - 使用轻量级主题

### 备用方案：
1. **Markdown查看器**：
   - 使用系统默认查看器
   - 导出为HTML
   - 使用浏览器查看

2. **其他工具**：
   - 使用Typora
   - 使用Mark Text
   - 使用VS Code

---

## 🎉 总结

### 推荐方案：
1. **Slides插件** - 最佳Obsidian原生体验
2. **Canvas功能** - 灵活的自定义选项
3. **PDF导出** - 通用兼容性
4. **Reveal.js** - 专业演示效果

### 使用建议：
- 根据演示场景选择合适的方案
- 提前测试所有功能
- 准备多种备用方案
- 熟悉快捷键操作

**祝您演示成功！** 🚀

