# -*- coding: utf-8 -*-
"""简单测试 - 验证领域模型"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_domain_models():
    print("=" * 60)
    print("测试领域模型")
    print("=" * 60)

    # 测试 Rule 实体
    print("\n[1/3] 测试 Rule 实体...")
    from app.domain.rules.rule import Rule
    from app.domain.rules.rule_variant import RuleVariant

    rule = Rule(
        rule_id="test-1",
        game="Test Game",
        version="v1.0",
        section="1.1",
        rule_text="This is a test rule",
        keywords=["test", "sample"],
        complexity="basic",
    )
    print(f"[OK] Rule 创建成功: {rule.rule_id}")
    print(f"     游戏: {rule.game}")
    print(f"     复杂度: {rule.complexity}")

    # 测试 searchable_text
    searchable = rule.searchable_text()
    print(f"[OK] 可搜索文本长度: {len(searchable)} 字符")

    # 测试 Judgement 实体
    print("\n[2/3] 测试 Judgement 实体...")
    from app.domain.rules.judgement import Judgement
    from datetime import datetime

    judgement = Judgement(
        judgement_id="jdg-001",
        user_id="user-123",
        game="Magic: The Gathering",
        scenario="Test scenario",
        ruling="Test ruling",
        confidence=0.85,
        related_rules=["mtg-cr-117"],
    )
    print(f"[OK] Judgement 创建成功: {judgement.judgement_id}")
    print(f"     游戏: {judgement.game}")
    print(f"     置信度: {judgement.confidence}")

    # 测试种子数据
    print("\n[3/3] 测试种子数据加载...")
    from app.infrastructure.persistence.seed_rules import build_seed_rules

    rules = build_seed_rules()
    print(f"[OK] 加载 {len(rules)} 条种子规则")

    # 统计各游戏规则数量
    games = {}
    for r in rules:
        games[r.game] = games.get(r.game, 0) + 1

    for game, count in games.items():
        print(f"     {game}: {count} 条")

    print("\n" + "=" * 60)
    print("[SUCCESS] 领域模型测试通过!")
    print("=" * 60)

if __name__ == "__main__":
    test_domain_models()
