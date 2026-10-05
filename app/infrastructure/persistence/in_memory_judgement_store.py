# -*- coding: utf-8 -*-
"""桌游裁定的进程内存储。后续可无缝替换为 SQLite 实现。"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from app.domain.rules.judgement import Judgement


class InMemoryJudgementStore:
    def __init__(self) -> None:
        self._items: dict[str, Judgement] = {}
        self._sequence = 0

    async def next_judgement_id(self) -> str:
        self._sequence += 1
        return f"JDG-{self._sequence:04d}"

    async def save(self, judgement: Judgement) -> None:
        self._items[judgement.judgement_id] = judgement

    async def find_by_id(self, judgement_id: str):
        return self._items.get(judgement_id)

    async def find_by_user(self, user_id: str, limit: int = 50) -> list[Judgement]:
        values = [item for item in self._items.values() if item.user_id == user_id]
        return list(reversed(values))[:limit]

    async def find(self, *, judgement_id: str | None = None, user_id: str = "", game: str | None = None, limit: int = 10) -> list[Judgement]:
        if judgement_id:
            item = await self.find_by_id(judgement_id)
            return [item] if item and (not user_id or item.user_id == user_id) else []
        values = await self.find_by_user(user_id, limit=1000)
        if game:
            values = [item for item in values if item.game == game]
        return values[:limit]
