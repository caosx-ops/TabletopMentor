"""规则版本差异用例测试。"""
import asyncio

from app.application.usecases.rule_version_compare import RuleVersionCompareUseCase
from app.domain.rules.rule import Rule
from app.domain.rules.rule_variant import RuleVariant
from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository


def test_compare_rule_versions_returns_change_summary():
    rule = Rule(
        rule_id="demo-1", game="Demo", version="2024", section="1",
        rule_text="旧规则文本", variants=[RuleVariant(
            variant_id="demo-1-2025", version="2025", rule_text="新规则文本",
            changes="新增限制", effective_date="2025-01-01",
        )],
    )
    result = asyncio.run(RuleVersionCompareUseCase(InMemoryRuleRepository([rule])).compare("demo-1", "2024", "2025"))
    assert result["changed"] is True
    assert result["from"]["rule_text"] == "旧规则文本"
    assert result["to"]["rule_text"] == "新规则文本"
