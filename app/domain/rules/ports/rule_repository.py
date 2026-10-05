# -*- coding: utf-8 -*-
"""RuleRepository 端口（仿照 ProductRepository）"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.rules.rule import Rule


class RuleRepository(ABC):
    """规则仓储接口"""

    @abstractmethod
    async def find_by_id(self, rule_id: str) -> Optional[Rule]:
        """按 ID 查询单个规则"""
        pass

    @abstractmethod
    async def find_by_ids(self, rule_ids: list[str]) -> list[Rule]:
        """按 ID 列表批量查询"""
        pass

    @abstractmethod
    async def list_all(self) -> list[Rule]:
        """列出所有规则"""
        pass

    @abstractmethod
    async def find_by_game(self, game: str) -> list[Rule]:
        """按游戏查询规则"""
        pass
