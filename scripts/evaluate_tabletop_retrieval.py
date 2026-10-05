"""离线规则检索评测：不调用模型，只验证命中规则 ID。"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.application.usecases.rule_search import RuleSearchUseCase
from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository


CASES = [
    {"query": "优先权", "game": "Magic: The Gathering", "expected": "mtg-cr-117"},
    {"query": "对手施放瞬间", "game": "Magic: The Gathering", "expected": "mtg-cr-307"},
    {"query": "反应动作", "game": "D&D 5e", "expected": "dnd5e-phb-190"},
    {"query": "技能检定难度", "game": "Arkham Horror LCG", "expected": "ah-rrg-skill-test"},
]


async def evaluate() -> dict:
    use_case = RuleSearchUseCase(InMemoryRuleRepository())
    rows = []
    for case in CASES:
        hits = await use_case.search(case["query"], top_k=5, filters={"game": case["game"]})
        ids = [rule.rule_id for rule in hits]
        rows.append({**case, "hits": ids, "pass": case["expected"] in ids})
    passed = sum(row["pass"] for row in rows)
    return {"passed": passed, "total": len(rows), "recall_at_5": passed / len(rows), "cases": rows}


def main() -> int:
    result = asyncio.run(evaluate())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
