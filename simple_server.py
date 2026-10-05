# -*- coding: utf-8 -*-
"""简单的规则 API 测试服务器（独立运行）"""
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.application.usecases.rule_search import RuleSearchUseCase
from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository

app = FastAPI(title="TabletopMentor Rules API")
repo = InMemoryRuleRepository()
search = RuleSearchUseCase(repo)
judgements: list[dict] = []


class RuleQuery(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    game: str | None = None
    complexity: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class JudgementCreate(BaseModel):
    game: str = Field(min_length=1, max_length=120)
    scenario: str = Field(min_length=1, max_length=2000)
    ruling: str = Field(min_length=1, max_length=4000)
    confidence: float = Field(ge=0, le=1)
    related_rules: list[str] = Field(default_factory=list)
    notes: str = ""

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "TabletopMentor"}


@app.get("/api/rules/health")
async def rules_health():
    """规则API健康检查"""
    return {"status": "ok", "service": "Rules API"}


@app.post("/api/rules/query")
async def query_rules(request: RuleQuery):
    """查询规则，支持游戏、复杂度过滤。"""
    try:
        query = request.query
        filters = {}
        game = request.game
        top_k = request.top_k
        filters = {}
        if game:
            filters["game"] = game
        if request.complexity:
            filters["complexity"] = request.complexity

        # 执行检索
        results = await search.search(query=query, top_k=top_k, filters=filters)

        # 格式化响应
        hits = [rule_to_dict(r) for r in results]

        return {
            "hits": hits,
            "total": len(hits),
            "query_normalized": query,
            "filters_applied": filters,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rules/games/{game}/rules")
async def list_game_rules(game: str):
    rules = await search.search_by_game(game)
    return {"game": game, "rules": [rule_to_dict(r) for r in rules], "total": len(rules)}


@app.get("/api/rules/{rule_id}")
async def get_rule(rule_id: str):
    """获取规则详情"""
    try:
        rule = await search.search_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")

        return rule_to_dict(rule)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def rule_to_dict(rule):
    return {
        "rule_id": rule.rule_id, "game": rule.game, "version": rule.version,
        "section": rule.section, "rule_text": rule.rule_text, "keywords": rule.keywords,
        "complexity": rule.complexity, "source_language": rule.source_language,
        "translations": rule.translations, "related_rules": rule.related_rules,
        "common_mistakes": rule.common_mistakes, "examples": rule.examples,
        "source_url": rule.source_url, "updated_at": rule.updated_at,
    }


@app.post("/api/judgements", status_code=201)
async def create_judgement(request: JudgementCreate):
    item = request.model_dump()
    item.update({
        "judgement_id": f"JDG-{len(judgements) + 1:04d}",
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    judgements.append(item)
    return item


@app.get("/api/judgements")
async def list_judgements():
    return {"judgements": list(reversed(judgements)), "total": len(judgements)}


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("TabletopMentor Rules API 启动中...")
    print("=" * 60)
    print("API 地址: http://127.0.0.1:8000")
    print("文档地址: http://127.0.0.1:8000/docs")
    print("健康检查: curl http://127.0.0.1:8000/health")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
