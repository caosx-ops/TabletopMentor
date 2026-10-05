# -*- coding: utf-8 -*-
"""RuleSearchTool - 规则检索工具

TabletopMentor 的核心工具，负责检索桌游规则库。
基于原 product_search_tool 改造，保留检索架构。
"""
from __future__ import annotations

from typing import Any, Optional

from agentscope.tool import FunctionTool


def build_rule_search_tool(rule_search_use_case: Any) -> FunctionTool:
    """构建规则检索工具

    Args:
        rule_search_use_case: 规则检索用例（RuleSearchUseCase）

    Returns:
        AgentScope FunctionTool
    """

    async def rule_search_tool(
        query: str,
        game: Optional[str] = None,
        complexity: Optional[str] = None,
        top_k: int = 5,
        rule_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """检索桌游规则库

        Args:
            query: 规则查询（如"优先权机制"、"战斗步骤"）
            game: 游戏名称过滤（如"Magic: The Gathering"、"D&D 5e"）
            complexity: 复杂度过滤（basic/intermediate/advanced）
            top_k: 返回规则数量，默认 5
            rule_id: 精确查询特定规则ID（如"mtg-cr-117"）

        Returns:
            {
                "hits": [规则卡片列表],
                "total": 召回总数,
                "query_normalized": 标准化查询,
                "filters_applied": {应用的过滤条件}
            }
        """
        try:
            # 精确 ID 查询
            if rule_id:
                result = await rule_search_use_case.search_by_id(rule_id)
                if result:
                    return {
                        "hits": [_format_rule_card(result)],
                        "total": 1,
                        "query_normalized": f"rule_id:{rule_id}",
                        "filters_applied": {"rule_id": rule_id},
                    }
                return {
                    "hits": [],
                    "total": 0,
                    "query_normalized": f"rule_id:{rule_id}",
                    "error": f"规则 {rule_id} 不存在",
                }

            # 语义检索
            filters = {}
            if game:
                filters["game"] = game
            if complexity:
                filters["complexity"] = complexity

            results = await rule_search_use_case.search(
                query=query,
                top_k=top_k,
                filters=filters,
            )

            return {
                "hits": [_format_rule_card(r) for r in results],
                "total": len(results),
                "query_normalized": query,
                "filters_applied": filters,
            }

        except Exception as e:
            return {
                "hits": [],
                "total": 0,
                "error": f"检索失败：{str(e)}",
            }

    def _format_rule_card(rule: Any) -> dict[str, Any]:
        """格式化规则卡片（供前端展示）"""
        return {
            "rule_id": rule.rule_id,
            "game": rule.game,
            "version": rule.version,
            "section": rule.section,
            "rule_text": rule.rule_text,
            "keywords": rule.keywords,
            "complexity": rule.complexity,
            "source_language": rule.source_language,
            "translations": rule.translations,
            "related_rules": rule.related_rules,
            "common_mistakes": rule.common_mistakes,
            "examples": rule.examples,
            "source_url": rule.source_url,
            "updated_at": rule.updated_at,
            "variants": [
                {
                    "variant_id": variant.variant_id,
                    "version": variant.version,
                    "effective_date": variant.effective_date,
                    "deprecated": variant.deprecated,
                }
                for variant in rule.variants
            ],
        }

    return FunctionTool(
        rule_search_tool,
        name="rule_search_tool",
        description="检索桌游规则库。支持语义检索、游戏过滤和复杂度过滤。",
    )


def build_rule_version_compare_tool(repository: Any) -> FunctionTool:
    """构建规则版本比较工具，供规则检索 Agent 处理版本差异问题。"""
    from app.application.usecases.rule_version_compare import RuleVersionCompareUseCase

    use_case = RuleVersionCompareUseCase(repository)

    async def compare_rule_versions(rule_id: str, from_version: str, to_version: str) -> dict[str, Any]:
        try:
            return await use_case.compare(rule_id, from_version, to_version)
        except (KeyError, ValueError) as exc:
            return {"rule_id": rule_id, "changed": False, "error": str(exc)}

    return FunctionTool(
        compare_rule_versions,
        name="compare_rule_versions_tool",
        description="比较同一桌游规则在两个版本中的正文差异。必须先知道 rule_id 和两个版本标识。",
    )
