# -*- coding: utf-8 -*-
"""Judgement - 裁定记录

对应原 Order 概念，记录用户的规则咨询场景和裁定结果。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Judgement:
    """规则裁定记录"""

    judgement_id: str                   # 裁定唯一标识
    user_id: str                        # 用户ID
    game: str                           # 游戏名称
    scenario: str                       # 场景描述
    ruling: str                         # 裁定结果
    confidence: float                   # 置信度 0-1
    related_rules: list[str] = field(default_factory=list)  # 引用的规则ID
    approved: bool = False              # 用户是否确认采纳
    notes: str = ""                     # 备注
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.judgement_id:
            raise ValueError("Judgement.judgement_id required")
        if not self.user_id:
            raise ValueError("Judgement.user_id required")
        if not (0 <= self.confidence <= 1):
            raise ValueError(f"Judgement.confidence 必须在 0-1 之间：{self.confidence}")
