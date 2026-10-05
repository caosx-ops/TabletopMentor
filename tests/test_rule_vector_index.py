"""规则向量召回的离线契约测试。"""
import asyncio
from pathlib import Path

from app.application.usecases.rule_search import RuleSearchUseCase
from app.domain.rules.rule import Rule
from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository
from app.infrastructure.rules.vector_index import RuleVectorIndex


class FakeEmbedder:
    async def embed(self, text):
        return [1.0, 0.0] if "优先" in text else [0.0, 1.0]

    async def embed_batch(self, texts):
        return [[1.0, 0.0] if "优先" in text else [0.0, 1.0] for text in texts]


def test_rule_vector_recall_is_optional_and_persistent(tmp_path: Path):
    rules = [
        Rule(rule_id="a", game="Demo", version="1", section="1", rule_text="优先权规则"),
        Rule(rule_id="b", game="Demo", version="1", section="2", rule_text="战斗规则"),
    ]
    index = RuleVectorIndex(tmp_path / "vectors.json")
    use_case = RuleSearchUseCase(InMemoryRuleRepository(rules), embedder=FakeEmbedder(), vector_index=index, hybrid_enabled=True)
    hits = asyncio.run(use_case.search("优先权", top_k=1))
    assert hits[0].rule_id == "a"
    assert (tmp_path / "vectors.json").exists()
