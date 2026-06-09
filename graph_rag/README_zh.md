# GraphRAG 项目

基于 Microsoft GraphRAG 的扩展版本，支持 **PDF 远程解析（MinerU）**、**提示词自动生成**、**索引构建** 与 **Web 查询界面**。

## 目录结构

```
graph_rag/
├── graphrag/              # 核心源码（含 PDF 输入、api_dev 工具）
│   └── api_dev/           # 索引 / 提示词 / 查询 / FastAPI 服务
├── test_pdf/              # PDF 索引示例工程（settings.yaml + prompts）
├── pyproject.toml         # Poetry 依赖
└── poetry.lock
```

## 环境准备

```bash
cd graph_rag
cp .env.example .env   # 填入 API Key
poetry install
```

## 常用命令

```bash
# 1. 生成定制提示词
cd graphrag/api_dev
poetry run python graphrag_prompt_tune.py

# 2. 构建索引
poetry run python graphrag_indexing.py

# 3. 命令行查询
poetry run python graphrag_query.py

# 4. 启动 Web 查询界面
poetry run python graphrag_api.py
# 浏览器打开 http://127.0.0.1:9999/static/index.html
```

## PDF 索引说明

- 在 `test_pdf/settings.yaml` 中配置 `mineru_api_url` 等 MinerU 服务地址
- 将 PDF 放入 `test_pdf/input/`
- 解析后的 Markdown 默认保存在 `test_pdf/pdf_output/`

## 定制 UI

查询界面静态资源位于 `graphrag/api_dev/static/`：

- `css/theme.css` — 主题配色
- `css/index.css` — 布局样式
- `js/index.js` — 查询逻辑
- `js/sci-fi-lines.js` — 背景动效
