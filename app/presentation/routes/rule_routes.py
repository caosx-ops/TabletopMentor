# -*- coding: utf-8 -*-
"""规则 API 路由"""
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request

from app.presentation.schemas.rule_schemas import (
    RuleQueryRequest,
    RuleQueryResponse,
    RuleCard,
    JudgementRequest,
    JudgementResponse,
    JudgementDecision,
    RuleVersionSnapshot,
    RuleVersionCompareRequest,
    AgentRuleQueryRequest,
    AgentRuleQueryResponse,
)
from app.composition import Container

router = APIRouter(prefix="/api/rules", tags=["rules"])


async def get_container(request: Request) -> Container:
    """复用服务生命周期中的容器，避免每个请求重复打开本地 Qdrant。"""
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(status_code=503, detail="服务尚未就绪")
    return container


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "TabletopMentor Rules API"}


@router.get("/capabilities")
async def rule_capabilities(container: Container = Depends(get_container)):
    """报告规则检索当前真实能力，避免把未配置的外部服务误报为已启用。"""
    from app.application.usecases.rule_search import RuleSearchUseCase
    use_case = RuleSearchUseCase(container.rule_repo)
    return {"rules": len(await container.rule_repo.list_all()), "retrieval": use_case.capabilities()}


@router.post("/query", response_model=RuleQueryResponse)
async def query_rules(
    request: RuleQueryRequest,
    container: Container = Depends(get_container)
):
    """查询规则

    示例:
        POST /api/rules/query
        {
            "query": "优先权",
            "game": "Magic: The Gathering",
            "top_k": 5
        }
    """
    try:
        # 使用规则检索用例
        from app.application.usecases.rule_search import RuleSearchUseCase

        search_use_case = RuleSearchUseCase(container.rule_repo)

        # 构建过滤条件
        filters = {}
        if request.game:
            filters["game"] = request.game
        if request.complexity:
            filters["complexity"] = request.complexity

        # 执行检索
        results = await search_use_case.search(
            query=request.query,
            top_k=request.top_k,
            filters=filters,
        )

        # 格式化响应
        hits = [
            RuleCard(
                rule_id=r.rule_id,
                game=r.game,
                version=r.version,
                section=r.section,
                rule_text=r.rule_text,
                keywords=r.keywords,
                complexity=r.complexity,
                source_language=r.source_language,
                translations=r.translations,
                related_rules=r.related_rules,
                common_mistakes=r.common_mistakes,
                examples=r.examples,
                source_url=r.source_url or "",
                updated_at=r.updated_at or "",
                variants=[v.__dict__ for v in r.variants],
            )
            for r in results
        ]

        return RuleQueryResponse(
            hits=hits,
            total=len(hits),
            query_normalized=request.query,
            filters_applied=filters,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/agent/query", response_model=AgentRuleQueryResponse)
async def agent_query(request: AgentRuleQueryRequest, container: Container = Depends(get_container)):
    """通过真实 RuleAdvisor Agent 处理自然语言问题，返回最终回答。"""
    from app.application.agents.orchestrator import SubmitIntentInput
    try:
        result = await container.orchestrator.handle_intent(SubmitIntentInput(
            shopping_session_id=request.session_id,
            buyer_id=request.user_id,
            locale=request.locale,
            currency=request.currency,
            raw_query=request.query.strip(),
        ), use_semantic_cache=False)
        return AgentRuleQueryResponse(
            session_id=result.shopping_session_id,
            final_text=result.final_text,
            error=result.error,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent 执行失败: {type(exc).__name__}") from exc


@router.get("/judgements")
async def list_judgements_early(container: Container = Depends(get_container), user_id: str = "api", game: Optional[str] = None, limit: int = 20):
    items = await container.judgement_store.find(user_id=user_id, game=game, limit=max(1, min(limit, 50)))
    return {"judgements": [
        {"judgement_id": item.judgement_id, "game": item.game, "scenario": item.scenario,
         "ruling": item.ruling, "confidence": item.confidence, "related_rules": item.related_rules,
         "notes": item.notes, "approved": item.approved, "status": "approved" if item.approved else "pending", "created_at": item.created_at.isoformat()}
        for item in items
    ], "total": len(items)}


@router.get("/{rule_id}/versions", response_model=list[RuleVersionSnapshot])
async def list_rule_versions(rule_id: str, container: Container = Depends(get_container)):
    """列出规则当前版本及历史变体。"""
    from app.application.usecases.rule_version_compare import RuleVersionCompareUseCase
    versions = await RuleVersionCompareUseCase(container.rule_repo).list_versions(rule_id)
    if not versions:
        raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")
    return [RuleVersionSnapshot(**item.__dict__) for item in versions]


@router.post("/{rule_id}/versions/compare")
async def compare_rule_versions(
    rule_id: str,
    request: RuleVersionCompareRequest,
    container: Container = Depends(get_container),
):
    """比较同一规则的两个版本，供 Agent 引用版本差异。"""
    from app.application.usecases.rule_version_compare import RuleVersionCompareUseCase
    try:
        return await RuleVersionCompareUseCase(container.rule_repo).compare(
            rule_id, request.from_version, request.to_version,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/{rule_id}", response_model=RuleCard)
async def get_rule(
    rule_id: str,
    container: Container = Depends(get_container)
):
    """按ID获取规则详情"""
    try:
        from app.application.usecases.rule_search import RuleSearchUseCase

        search_use_case = RuleSearchUseCase(container.rule_repo)
        rule = await search_use_case.search_by_id(rule_id)

        if not rule:
            raise HTTPException(status_code=404, detail=f"规则 {rule_id} 不存在")

        return RuleCard(
            rule_id=rule.rule_id,
            game=rule.game,
            version=rule.version,
            section=rule.section,
            rule_text=rule.rule_text,
            keywords=rule.keywords,
            complexity=rule.complexity,
            source_language=rule.source_language,
            translations=rule.translations,
            related_rules=rule.related_rules,
            common_mistakes=rule.common_mistakes,
            examples=rule.examples,
            source_url=rule.source_url or "",
            updated_at=rule.updated_at or "",
            variants=[v.__dict__ for v in rule.variants],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/games/{game}/rules")
async def list_game_rules(
    game: str,
    container: Container = Depends(get_container)
):
    """列出某个游戏的所有规则"""
    try:
        from app.application.usecases.rule_search import RuleSearchUseCase

        search_use_case = RuleSearchUseCase(container.rule_repo)
        rules = await search_use_case.search_by_game(game)

        hits = [
            RuleCard(
                rule_id=r.rule_id,
                game=r.game,
                version=r.version,
                section=r.section,
                rule_text=r.rule_text,
                keywords=r.keywords,
                complexity=r.complexity,
                source_language=r.source_language,
                translations=r.translations,
                related_rules=r.related_rules,
                common_mistakes=r.common_mistakes,
                examples=r.examples,
                source_url=r.source_url or "",
                updated_at=r.updated_at or "",
                variants=[v.__dict__ for v in r.variants],
            )
            for r in rules
        ]

        return {
            "game": game,
            "rules": hits,
            "total": len(hits),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/judgement", response_model=JudgementResponse)
async def create_judgement(
    request: JudgementRequest,
    container: Container = Depends(get_container)
):
    """创建裁定建议（MVP版本）"""
    try:
        from datetime import datetime, timezone
        from app.domain.rules.judgement import Judgement
        judgement_id = await container.judgement_store.next_judgement_id()
        await container.judgement_store.save(Judgement(
            judgement_id=judgement_id, user_id=request.user_id, game=request.game,
            scenario=request.scenario, ruling=request.ruling, confidence=request.confidence,
            related_rules=request.related_rules, notes=request.notes,
        ))
        return JudgementResponse(
            judgement_id=judgement_id,
            game=request.game,
            scenario=request.scenario,
            ruling=request.ruling,
            confidence=request.confidence,
            related_rules=request.related_rules,
            notes=request.notes,
            status="pending",
            message=f"裁定 {judgement_id} 已创建，等待确认",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建裁定失败: {str(e)}")

@router.post("/judgement/{judgement_id}/decision")
async def decide_judgement(judgement_id: str, request: JudgementDecision, container: Container = Depends(get_container)):
    if not await container.judgement_store.set_approved(judgement_id, request.approved):
        raise HTTPException(status_code=404, detail=f"裁定 {judgement_id} 不存在")
    item = await container.judgement_store.find_by_id(judgement_id)
    return {"judgement_id": judgement_id, "status": "approved" if request.approved else "rejected", "approved": request.approved, "ruling": item.ruling}


