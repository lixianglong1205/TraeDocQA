# 智能文档问答系统

基于文档的智能问答应用，支持用户上传文档（PDF/TXT），自动提取FAQ，并通过语义检索与大语言模型提供精准问答服务。

## 功能特性

- 支持PDF和TXT文档上传
- 自动提取文档中的问题-答案对（FAQ）
- 基于向量检索的语义搜索
- 流式对话界面
- 问题分类与意图识别
- 计算功能支持

## 技术架构

- **前端**: Streamlit
- **LLM框架**: LangChain
- **向量数据库**: Chroma
- **嵌入模型**: OpenAI Embeddings
- **依赖管理**: uv

## 环境要求

- Python 3.9+
- uv (用于依赖管理)

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

或者直接安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件并添加OpenAI API密钥：

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动应用

```bash
uv run streamlit run app.py
```

或

```bash
streamlit run app.py
```

### 4. 使用应用

1. 打开浏览器访问 `http://localhost:8501`
2. 上传PDF或TXT文档
3. 等待文档解析和FAQ提取
4. 切换到问答页面开始提问

## 项目结构

```
src/
├── api/           # API接口
├── data/          # 数据处理模块
│   └── parser.py  # 文档解析器
├── database/      # 数据库相关
│   └── vector_store.py  # 向量存储
├── llm/           # 大语言模型相关
│   ├── faq_extractor.py  # FAQ提取器
│   └── qa_processor.py   # 问答处理器
├── ui/            # 用户界面
│   ├── main.py         # 主界面
│   ├── upload_page.py  # 上传页面
│   └── chat_page.py    # 聊天页面
└── utils/         # 工具函数
    └── config.py       # 配置管理
```

## 注意事项

- 确保网络可以访问OpenAI API
- 文档大小会影响处理时间
- API密钥请妥善保管，不要泄露

## 许可证

MIT