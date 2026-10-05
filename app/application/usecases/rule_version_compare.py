# -*- coding: utf-8 -*-
"""规则版本比较用例。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleVersionSnapshot:
    version: str
    rule_text: str
    effective_date: str = ""
    deprecated: bool = False
    variant_id: str = "current"


class RuleVersionCompareUseCase:
    """把 Rule 的当前版本和 RuleVariant 统一成可比较快照。"""

    def __init__(self, repository: Any) -> None:
        self._repository = repository

    async def list_versions(self, rule_id: str) -> list[RuleVersionSnapshot]:
        rule = await self._repository.find_by_id(rule_id)
        if rule is None:
            return []
        versions = [RuleVersionSnapshot(version=rule.version, rule_text=rule.rule_text)]
        versions.extend(
            RuleVersionSnapshot(
                variant_id=variant.variant_id,
                version=variant.version,
                rule_text=variant.rule_text,
                effective_date=variant.effective_date,
                deprecated=variant.deprecated,
            )
            for variant in rule.variants
        )
        # 同一版本可能同时作为当前版本和变体存在，避免 API 返回重复项。
        unique: dict[tuple[str, str], RuleVersionSnapshot] = {}
        for item in versions:
            unique[(item.version, item.rule_text)] = item
        return list(unique.values())

    async def compare(self, rule_id: str, from_version: str, to_version: str) -> dict:
        versions = await self.list_versions(rule_id)
        if not versions:
            raise KeyError(rule_id)
        by_version = {item.version: item for item in versions}
        if from_version not in by_version or to_version not in by_version:
            missing = from_version if from_version not in by_version else to_version
            raise ValueError(f"规则 {rule_id} 不存在版本 {missing}")
        source = by_version[from_version]
        target = by_version[to_version]
        return {
            "rule_id": rule_id,
            "from": source.__dict__,
            "to": target.__dict__,
            "changed": source.rule_text != target.rule_text,
            "change_summary": "规则正文发生变化" if source.rule_text != target.rule_text else "规则正文未变化",
        }
