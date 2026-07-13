# research-agent-project

智研--AI学术研究助手
输入问题 → AI 自动拆关键词 → 搜资料 → 生成学术报告。

## 技术栈

后端：FastAPI
数据库：SQLite
AI：Deepseek API
前端：原生HTML + CSS

## 怎么跑

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

根目录新建 `.env` 文件，填入 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

## 项目结构

```
├── main.py
├── backend/auth.py      # 登录注册
├── database/            # 数据库
├── ai_core/             # AI 核心
│   ├── planner.py       # 拆问题
│   ├── searcher.py      # 搜资料
│   └── writer.py        # 写报告
└── frontend/index.html  # 页面
```

## 遇到的问题

- 维基百科访问不了 → 换成百度百科
- 流式调起来太麻烦 → 换成轮询

## 交了，能跑
