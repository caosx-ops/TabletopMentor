# -*- coding: utf-8 -*-
"""SQLite 裁定存储，服务重启后保留记录。"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import aiosqlite
from app.domain.rules.judgement import Judgement

class SqliteJudgementStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    async def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS judgements (
                judgement_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, game TEXT NOT NULL,
                scenario TEXT NOT NULL, ruling TEXT NOT NULL, confidence REAL NOT NULL,
                related_rules TEXT NOT NULL, approved INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending', notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
            )""")
            await db.commit()

    async def next_judgement_id(self) -> str:
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT COUNT(*) FROM judgements") as cur:
                count = (await cur.fetchone())[0]
        return f"JDG-{count + 1:04d}"

    async def save(self, judgement: Judgement, status: str = "pending") -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""INSERT OR REPLACE INTO judgements
                (judgement_id,user_id,game,scenario,ruling,confidence,related_rules,approved,status,notes,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (judgement.judgement_id, judgement.user_id, judgement.game,
                judgement.scenario, judgement.ruling, judgement.confidence, json.dumps(judgement.related_rules, ensure_ascii=False),
                int(judgement.approved), status, judgement.notes, judgement.created_at.isoformat()))
            await db.commit()

    def _row(self, row) -> Judgement:
        return Judgement(judgement_id=row[0], user_id=row[1], game=row[2], scenario=row[3], ruling=row[4],
            confidence=row[5], related_rules=json.loads(row[6]), approved=bool(row[7]), notes=row[9],
            created_at=datetime.fromisoformat(row[10]))

    async def find_by_id(self, judgement_id: str):
        async with aiosqlite.connect(self.path) as db:
            async with db.execute("SELECT judgement_id,user_id,game,scenario,ruling,confidence,related_rules,approved,status,notes,created_at FROM judgements WHERE judgement_id=?", (judgement_id,)) as cur:
                row = await cur.fetchone()
        return self._row(row) if row else None

    async def find_by_user(self, user_id: str, limit: int = 50) -> list[Judgement]:
        return await self.find(user_id=user_id, limit=limit)

    async def find(self, *, judgement_id=None, user_id="", game=None, limit=10):
        async with aiosqlite.connect(self.path) as db:
            sql = "SELECT judgement_id,user_id,game,scenario,ruling,confidence,related_rules,approved,status,notes,created_at FROM judgements WHERE 1=1"
            args = []
            if judgement_id: sql += " AND judgement_id=?"; args.append(judgement_id)
            if user_id: sql += " AND user_id=?"; args.append(user_id)
            if game: sql += " AND game=?"; args.append(game)
            sql += " ORDER BY created_at DESC LIMIT ?"; args.append(limit)
            async with db.execute(sql, args) as cur: rows = await cur.fetchall()
        return [self._row(row) for row in rows]

    async def set_approved(self, judgement_id: str, approved: bool) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("UPDATE judgements SET approved=?, status=? WHERE judgement_id=?", (int(approved), "approved" if approved else "rejected", judgement_id))
            await db.commit()
            return cur.rowcount > 0

    async def close(self) -> None:
        return None
