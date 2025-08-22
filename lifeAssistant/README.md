# 智能天气建议系统

基于AI技术的天气预报建议系统，提供穿衣、出行、健康和活动建议。

## 功能特性

- **穿衣指数**：根据温度推荐服装
- **出行建议**：结合天气推荐出行方式  
- **健康提醒**：针对敏感人群的健康建议
- **活动规划**：推荐适合的室内外活动
- **智能对话**：支持用户反馈和重新生成建议

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 生成语料库
```bash
python generate_corpus.py
```

### 启动Web应用
```bash
python app.py
```

访问 http://localhost:5000 使用系统

## 项目结构

- `generate_corpus.py` - 语料库生成器
- `weather_bert.py` - BERT模型
- `chat_system.py` - 对话系统
- `app.py` - Flask Web应用
- `templates/` - 前端界面

## 使用方法

1. 输入天气信息（温度、天气、空气质量）
2. 获取智能建议
3. 如不满意可获取替代建议
4. 使用对话功能进行交互

## 技术特点

- 使用faker生成训练数据
- 基于BERT的智能建议
- 支持用户反馈学习
- 现代化Web界面
