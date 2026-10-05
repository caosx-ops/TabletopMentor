# -*- coding: utf-8 -*-
"""RuleVariant - 规则版本/变体

对应原 SKU 概念，表示同一规则在不同版本/扩展中的差异。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleVariant:
    """规则变体（不同版本、扩展的规则差异）"""

    variant_id: str          # 变体唯一标识
    version: str             # 版本标识（如 "CR 2024-03-08"）
    rule_text: str           # 该版本的规则文本
    changes: str = ""        # 与前版本的变更说明
    effective_date: str = "" # 生效日期
    deprecated: bool = False # 是否已废弃

    def __post_init__(self) -> None:
        if not self.variant_id:
            raise ValueError("RuleVariant.variant_id required")
        if not self.version:
            raise ValueError("RuleVariant.version required")
