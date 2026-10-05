# -*- coding: utf-8 -*-
"""基于 OpenAI 兼容 embedding 的轻量规则向量索引。"""
from __future__ import annotations
import json
import math
from pathlib import Path
from typing import Any


class RuleVectorIndex:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._vectors: dict[str, list[float]] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if self._path.exists():
            try:
                body = json.loads(self._path.read_text(encoding="utf-8"))
                self._vectors = {str(k): [float(v) for v in values] for k, values in body.items()}
            except (OSError, ValueError, TypeError):
                self._vectors = {}

    async def ensure_built(self, rules: list[Any], embedder: Any) -> None:
        self._load()
        missing = [rule for rule in rules if rule.rule_id not in self._vectors]
        if not missing:
            return
        vectors = await embedder.embed_batch([rule.searchable_text() for rule in missing])
        if len(vectors) != len(missing):
            raise RuntimeError("规则 embedding 返回数量与规则数量不一致")
        for rule, vector in zip(missing, vectors):
            self._vectors[rule.rule_id] = [float(value) for value in vector]
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._vectors, ensure_ascii=False), encoding="utf-8")

    async def search(self, embedding: list[float], top_k: int, allowed_ids: set[str] | None = None) -> list[tuple[str, float]]:
        self._load()
        scores = []
        for rule_id, vector in self._vectors.items():
            if allowed_ids is not None and rule_id not in allowed_ids or len(vector) != len(embedding):
                continue
            left = math.sqrt(sum(value * value for value in embedding))
            right = math.sqrt(sum(value * value for value in vector))
            score = sum(a * b for a, b in zip(embedding, vector)) / (left * right) if left and right else 0.0
            scores.append((rule_id, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]
