# -*- coding: utf-8 -*-
"""JudgementTools - 裁定工具

基于原 order_tools 改造，用于创建和查询规则裁定记录。
"""
from __future__ import annotations

from typing import Any, Optional
from datetime import datetime, timezone
from app.domain.rules.judgement import Judgement

from agentscope.tool import FunctionTool


def build_create_judgement_tool(judgement_store: Any, user_id: str | None = None) -> FunctionTool:
    """构建创建裁定工具"""

    async def create_judgement_tool(
        game: str,
        scenario: str,
        ruling: str,
        confidence: float,
        related_rules: list[str],
        notes: str = "",
    ) -> dict[str, Any]:
        """创建规则裁定建议（需用户确认）

        Args:
            game: 游戏名称（如"Magic: The Gathering"）
            scenario: 场景描述
            ruling: 裁定建议内容
            confidence: 置信度（0-1，如 0.85 表示 85% 确信）
            related_rules: 引用的规则 ID 列表（如 ["mtg-cr-117", "mtg-cr-608"]）
            notes: 备注说明（可选）

        Returns:
            {
                "judgement_id": "裁定ID",
                "status": "pending_approval",
                "message": "裁定已生成，等待玩家确认"
            }
        """
        try:
            # 验证置信度
            if not 0 <= confidence <= 1:
                return {
                    "error": "置信度必须在 0-1 之间",
                    "status": "failed",
                }

            # 验证必填字段
            if not game or not scenario or not ruling:
                return {
                    "error": "游戏、场景和裁定内容不能为空",
                    "status": "failed",
                }

            from app.infrastructure.context import ShoppingContext
            effective_user_id = user_id or (ShoppingContext.current().buyer_id if ShoppingContext.current() else "agent")
            judgement_id = await judgement_store.next_judgement_id()
            judgement = Judgement(
                judgement_id=judgement_id, user_id=effective_user_id, game=game,
                scenario=scenario, ruling=ruling, confidence=confidence,
                related_rules=related_rules, notes=notes,
            )
            await judgement_store.save(judgement)
            return {
                "judgement_id": judgement_id,
                "game": game,
                "scenario": scenario,
                "ruling": ruling,
                "confidence": confidence,
                "related_rules": related_rules,
                "notes": notes,
                "status": "saved",
                "message": f"裁定 {judgement_id} 已保存",
            }

        except Exception as e:
            return {
                "error": f"创建裁定失败: {str(e)}",
                "status": "failed",
            }

    return FunctionTool(
        create_judgement_tool,
        name="create_judgement_tool",
        description="创建规则裁定建议，需要玩家确认后才会保存到历史记录。",
    )


def build_query_judgement_tool(judgement_store: Any, user_id: str | None = None) -> FunctionTool:
    """构建查询裁定工具"""

    async def query_judgement_tool(
        judgement_id: Optional[str] = None,
        game: Optional[str] = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """查询裁定历史

        Args:
            judgement_id: 精确查询裁定ID
            game: 按游戏过滤
            limit: 返回数量限制

        Returns:
            {
                "judgements": [裁定记录列表],
                "total": 总数
            }
        """
        try:
            from app.infrastructure.context import ShoppingContext
            effective_user_id = user_id or (ShoppingContext.current().buyer_id if ShoppingContext.current() else "agent")
            items = await judgement_store.find(judgement_id=judgement_id, user_id=effective_user_id, game=game, limit=max(1, min(limit, 50)))
            return {
                "judgements": [
                    {"judgement_id": item.judgement_id, "game": item.game, "scenario": item.scenario,
                     "ruling": item.ruling, "confidence": item.confidence,
                     "related_rules": item.related_rules, "notes": item.notes,
                     "approved": item.approved, "created_at": item.created_at.isoformat()}
                    for item in items
                ],
                "total": len(items),
            }

        except Exception as e:
            return {
                "error": f"查询裁定失败: {str(e)}",
                "judgements": [],
                "total": 0,
            }

    return FunctionTool(
        query_judgement_tool,
        name="query_judgement_tool",
        description="查询裁定历史记录。",
    )


def build_game_knowledge_tool(knowledge_base: Any) -> FunctionTool:
    """构建游戏知识工具（基于原 category_insight_tool）"""

    async def game_knowledge_tool(
        game: str,
        topic: str,
    ) -> dict[str, Any]:
        """查询游戏机制知识库

        Args:
            game: 游戏名称（如"Magic: The Gathering"）
            topic: 知识主题（如"堆叠机制"、"战斗流程"）

        Returns:
            {
                "game": 游戏名称,
                "topic": 主题,
                "knowledge": 知识内容,
                "references": 相关规则引用
            }
        """
        try:
            from app.infrastructure.rag.category_knowledge import keyword_fallback_insights
            insights = keyword_fallback_insights(f"{game} {topic}", top_k=3)
            return {
                "game": game,
                "topic": topic,
                "knowledge": "\n\n".join(item["content"] for item in insights) if insights else f"暂未找到 {game} 的 {topic} 知识。",
                "references": [item["source"] for item in insights],
                "total": len(insights),
            }

        except Exception as e:
            return {
                "error": f"查询知识失败: {str(e)}",
            }

    return FunctionTool(
        game_knowledge_tool,
        name="game_knowledge_tool",
        description="查询游戏机制知识库，了解核心规则、常见误区和裁定案例。",
    )
