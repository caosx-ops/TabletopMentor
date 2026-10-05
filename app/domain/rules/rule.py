# -*- coding: utf-8 -*-
"""Rule 聚合根

TabletopMentor 将桌游规则建模为 Rule（规则条目）+ RuleVariant（多个版本），
携带游戏、章节、关键术语等结构化属性。
RuleSearchAgent 召回的"候选集"传递的就是 Rule 卡片，JudgeAgent 进行裁定时引用具体规则。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domain.rules.rule_variant import RuleVariant


@dataclass
class Rule:
    """桌游规则条目"""

    rule_id: str                        # 唯一标识
    game: str                           # 游戏名称（原 platform）
    version: str                        # 当前版本（原 category）
    section: str                        # 章节编号（原 subcategory）
    rule_text: str                      # 规则正文（原 description）
    keywords: list[str] = field(default_factory=list)  # 关键术语
    complexity: str = "basic"           # 复杂度：basic/intermediate/advanced（原 price_range）
    source_language: str = "zh-CN"      # 源语言
    translations: dict[str, str] = field(default_factory=dict)  # 多语言翻译
    variants: list[RuleVariant] = field(default_factory=list)   # 不同版本
    related_rules: list[str] = field(default_factory=list)      # 关联规则ID
    common_mistakes: list[str] = field(default_factory=list)    # 常见误区
    examples: list[str] = field(default_factory=list)           # 应用场景示例

    # 扩展字段（保留原商品模型的多语言支持结构）
    source_url: str = ""                # 官方规则来源链接
    updated_at: str = ""                # 更新时间

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("Rule.rule_id required")
        if not self.game:
            raise ValueError("Rule.game required")
        if self.complexity not in ("basic", "intermediate", "advanced"):
            raise ValueError(f"Rule.complexity 必须是 basic/intermediate/advanced：{self.rule_id}")

    def primary_variant(self) -> Optional[RuleVariant]:
        """返回主要版本（当前版本）"""
        return self.variants[0] if self.variants else None

    def find_variant(self, variant_id: str) -> Optional[RuleVariant]:
        """查找指定版本"""
        return next((v for v in self.variants if v.variant_id == variant_id), None)

    def searchable_text(self) -> str:
        """召回用的可检索文本：游戏 + 章节 + 规则文本 + 关键术语 + 常见误区"""
        keywords_text = " ".join(self.keywords)
        mistakes_text = " ".join(self.common_mistakes)
        examples_text = " ".join(self.examples)

        return " ".join([
            self.game,
            self.version,
            self.section,
            self.rule_text,
            keywords_text,
            mistakes_text,
            examples_text,
        ])
