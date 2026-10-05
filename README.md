# TabletopMentor

TabletopMentor 是一个面向万智牌、D&D 5e 和阿卡姆惊悚等桌游场景的多 Agent 规则裁定系统，支持规则检索、版本比较、专家协作、裁定审批和流式响应。

## 核心能力

- **多 Agent 协作**：RuleAdvisor 负责任务拆解，RuleSearchAgent 和 JudgeAgent 负责规则检索与裁定建议。
- **规则检索**：中文片段拆分、BM25 词频/IDF 评分、关键词加权和游戏维度过滤；内置规则集离线 Recall@5 为 1.0。
- **裁定闭环**：SQLite 事务持久化用户级裁定，支持 `pending -> approved/rejected` 状态流转和历史查询。
- **可靠性治理**：循环检测、工具顺序校验、失败重试、超时熔断、Token 预算和上下文压缩；Redis 共享熔断状态并提供 Redis Stream 队列。
- **协议与观测**：提供 FastAPI API、AG-UI/SSE 流式接口和 OpenTelemetry 链路追踪。

## 技术栈

Python 3.11+、AgentScope 2.0、FastAPI、React、SQLite、Redis、BM25、OpenTelemetry、Docker Compose。

## 快速开始

复制 `.env.example` 为 `.env`，填写模型服务配置：

```dotenv
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=填写你的 API Key
LLM_MODEL=deepseek-chat
TABLETOP_MODE=1
REDIS_URL=redis://127.0.0.1:6379/0
```

启动规则 API：

```bash
python simple_server.py
```

启动完整 Agent 服务：

```bash
uv run uvicorn app.presentation.server:app --host 127.0.0.1 --port 8000
```

规则检索接口为 `POST /api/rules/query`，Agent 自然语言入口为 `POST /api/rules/agent/query`，接口文档位于 `/docs`。

## 验证

```bash
python -m pytest -q tests/test_tabletop_acceptance.py tests/test_rule_search.py tests/test_rule_version_compare.py
python -m scripts.evaluate_tabletop_retrieval
python -m compileall -q app scripts tests
```

端到端验收脚本为 `acceptance.ps1` 和 `acceptance.sh`。默认规则数据位于 `app/infrastructure/persistence/seed_rules.py`，也可通过 `TABLETOP_RULES_FILE` 导入规范化 JSONL 规则库。

## 目录结构

```text
app/                 Agent、领域模型、检索、持久化和 API
frontend/            React 桌游规则工作台
knowledge/           桌游机制知识
scripts/             规则校验与离线评测
tests/               领域、检索、接口和验收测试
docker/              Docker Compose 编排
```


