# -*- coding: utf-8 -*-
"""JudgementStore 端口（仿照 TradeStore）"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.rules.judgement import Judgement


class JudgementStore(ABC):
    """裁定存储接口"""

    @abstractmethod
    async def save(self, judgement: Judgement) -> None:
        """保存裁定记录"""
        pass

    @abstractmethod
    async def find_by_id(self, judgement_id: str) -> Optional[Judgement]:
        """按 ID 查询裁定"""
        pass

    @abstractmethod
    async def find_by_user(self, user_id: str, limit: int = 50) -> list[Judgement]:
        """查询用户的裁定历史"""
        pass

    @abstractmethod
    async def next_judgement_id(self) -> str:
        """生成下一个裁定ID"""
        pass
