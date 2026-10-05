# -*- coding: utf-8 -*-
"""InMemoryRuleRepository

开发态内存仓储实现。RuleRepository 由种子数据初始化。
"""
from __future__ import annotations

from typing import Optional

from app.domain.rules.ports.rule_repository import RuleRepository
from app.domain.rules.rule import Rule
from app.infrastructure.persistence.seed_rules import build_seed_rules


class InMemoryRuleRepository(RuleRepository):
    def __init__(self, rules: Optional[list[Rule]] = None) -> None:
        seed = rules if rules is not None else build_seed_rules()
        self._rules: dict[str, Rule] = {r.rule_id: r for r in seed}

    async def find_by_id(self, rule_id: str) -> Optional[Rule]:
        return self._rules.get(rule_id)

    async def find_by_ids(self, rule_ids: list[str]) -> list[Rule]:
        return [self._rules[rid] for rid in rule_ids if rid in self._rules]

    async def list_all(self) -> list[Rule]:
        return list(self._rules.values())

    async def find_by_game(self, game: str) -> list[Rule]:
        return [r for r in self._rules.values() if r.game == game]
