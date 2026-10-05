# -*- coding: utf-8 -*-
"""RuleSearchUseCase - 规则检索用例

基于原 CatalogSearchUseCase 改造，保留向量检索 + BM25 混合架构。
"""
from __future__ import annotations

import re
from typing import Any, Optional

from app.domain.rules.rule import Rule
from app.domain.rules.ports.rule_repository import RuleRepository


class RuleSearchUseCase:
    """规则检索用例"""

    def __init__(
        self,
        rule_repo: RuleRepository,
        embedder: Any = None,
        vector_index: Any = None,
        reranker: Any = None,
        hybrid_enabled: bool = False,
        vector_weight: float = 0.35,
    ) -> None:
        self._rule_repo = rule_repo
        self._embedder = embedder
        self._vector_index = vector_index
        self._reranker = reranker
        self._hybrid_enabled = hybrid_enabled
        self._vector_weight = vector_weight

    async def search_by_id(self, rule_id: str) -> Optional[Rule]:
        """按 ID 精确查询规则"""
        return await self._rule_repo.find_by_id(rule_id)

    def capabilities(self) -> dict[str, object]:
        """返回当前规则检索实际启用的能力，供健康检查和评测记录使用。"""
        return {
            "lexical": "bm25",
            "vector_enabled": bool(self._hybrid_enabled and self._embedder and self._vector_index),
            "reranker_enabled": self._reranker is not None,
            "fallback": "bm25",
        }

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[Rule]:
        """语义检索规则

        Args:
            query: 查询文本
            top_k: 返回数量
            filters: 过滤条件 {"game": "游戏名", "complexity": "复杂度"}

        Returns:
            规则列表
        """
        # 先执行结构化过滤，再计算轻量 BM25 风格词项分数。
        all_rules = await self._rule_repo.list_all()

        # 应用过滤器
        filtered = all_rules
        if filters:
            if "game" in filters:
                filtered = [r for r in filtered if r.game == filters["game"]]
            if "complexity" in filters:
                filtered = [
                    r for r in filtered if r.complexity == filters["complexity"]
                ]

        query_lower = query.lower().strip()
        # 中文问题通常没有空格；按连续中文片段和英文单词拆分，避免整句无法命中。
        terms = []
        for part in re.findall(r"[\u4e00-\u9fff]{2,}|[a-z0-9][a-z0-9:_-]*", query_lower):
            if re.fullmatch(r"[\u4e00-\u9fff]+", part):
                terms.extend(part[i:i + size] for size in (2, 3, 4) for i in range(max(0, len(part) - size + 1)))
            else:
                terms.append(part)
        if not terms:
            terms = [query_lower]
        vector_scores: dict[str, float] = {}
        if self._hybrid_enabled and self._embedder is not None and self._vector_index is not None:
            try:
                await self._vector_index.ensure_built(all_rules, self._embedder)
                vector_scores = dict(await self._vector_index.search(
                    await self._embedder.embed(query), max(top_k, 10), {rule.rule_id for rule in filtered},
                ))
            except Exception:
                # 外部服务不可用时保留 BM25 结果，规则查询不能因 embedding 失败而中断。
                vector_scores = {}
        import math
        tokenized_docs = [
            re.findall(r"[\u4e00-\u9fff]{2}|[a-z0-9][a-z0-9:_-]*", rule.searchable_text().lower())
            for rule in filtered
        ]
        avgdl = sum(len(tokens) for tokens in tokenized_docs) / max(1, len(tokenized_docs))
        term_df = {term: sum(term in set(tokens) for tokens in tokenized_docs) for term in set(terms)}
        scored = []
        for rule, doc_terms in zip(filtered, tokenized_docs):
            score = 0.0
            searchable = rule.searchable_text().lower()
            if query_lower and query_lower in searchable:
                score += 3
            # BM25 词频、逆文档频率和规则关键词额外加权。
            for term in terms:
                frequency = doc_terms.count(term)
                if frequency:
                    df = term_df.get(term, 0)
                    idf = max(0.0, math.log((len(filtered) - df + 0.5) / (df + 0.5) + 1))
                    score += idf * (frequency * 2.5) / (frequency + 1.5 * (0.25 + 0.75 * len(doc_terms) / max(1, avgdl)))
                if any(term in keyword.lower() or keyword.lower() in term for keyword in rule.keywords):
                    score += 1.0
            if vector_scores:
                score += self._vector_weight * vector_scores.get(rule.rule_id, 0.0)
            if score > 0:
                scored.append((score, rule))

        # 按分数排序
        scored.sort(key=lambda x: x[0], reverse=True)

        if self._reranker is not None and scored:
            try:
                candidates = scored[: max(top_k, 10)]
                rerank_scores = await self._reranker.rerank(
                    query, [rule.searchable_text() for _, rule in candidates],
                )
                if len(rerank_scores) == len(candidates):
                    scored = sorted(
                        zip(rerank_scores, [rule for _, rule in candidates]),
                        key=lambda item: item[0], reverse=True,
                    )
            except Exception:
                # 专用精排服务失败时沿用 BM25/向量融合结果。
                pass

        return [rule for _, rule in scored[:top_k]]

    async def search_by_game(self, game: str) -> list[Rule]:
        """按游戏查询所有规则"""
        return await self._rule_repo.find_by_game(game)
