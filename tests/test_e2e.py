# -*- coding: utf-8 -*-
"""端到端测试 - 完整流程验证"""
import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_end_to_end():
    """端到端测试"""
    print("=" * 60)
    print("TabletopMentor 端到端测试")
    print("=" * 60)

    passed = 0
    failed = 0

    # 测试1: 仓储层
    print("\n[测试1] 仓储层...")
    try:
        from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository

        repo = InMemoryRuleRepository()
        rules = await repo.list_all()
        assert len(rules) == 13, f"预期13条规则，实际{len(rules)}条"

        rule = await repo.find_by_id("mtg-cr-117")
        assert rule is not None, "按ID查询失败"
        assert rule.game == "Magic: The Gathering", "游戏名称错误"

        print("[OK] 仓储层测试通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 测试2: 用例层
    print("\n[测试2] 用例层...")
    try:
        from app.application.usecases.rule_search import RuleSearchUseCase

        search = RuleSearchUseCase(repo)

        # 语义检索
        results = await search.search(query="优先权", top_k=3)
        assert len(results) > 0, "语义检索失败"

        # 游戏过滤
        mtg_rules = await search.search(
            query="战斗",
            filters={"game": "Magic: The Gathering"}
        )
        for r in mtg_rules:
            assert r.game == "Magic: The Gathering", "过滤失败"

        print("[OK] 用例层测试通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 测试3: 工具函数逻辑
    print("\n[测试3] 工具函数逻辑...")
    try:
        # 模拟工具调用
        query_result = await search.search(query="先攻", top_k=5)

        # 格式化输出（模拟工具返回）
        tool_output = {
            "hits": [{"rule_id": r.rule_id, "game": r.game} for r in query_result],
            "total": len(query_result),
        }

        assert "hits" in tool_output, "输出格式错误"
        assert "total" in tool_output, "输出格式错误"
        assert tool_output["total"] > 0, "未找到结果"

        print("[OK] 工具函数逻辑通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 测试4: 多游戏支持
    print("\n[测试4] 多游戏支持...")
    try:
        games = ["Magic: The Gathering", "D&D 5e", "Arkham Horror LCG"]
        for game in games:
            rules = await search.search_by_game(game)
            assert len(rules) > 0, f"{game} 无规则"
            print(f"  {game}: {len(rules)} 条规则")

        print("[OK] 多游戏支持通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 测试5: 数据完整性
    print("\n[测试5] 数据完整性...")
    try:
        all_rules = await repo.list_all()

        for rule in all_rules:
            # 必填字段检查
            assert rule.rule_id, "rule_id不能为空"
            assert rule.game, "game不能为空"
            assert rule.section, "section不能为空"
            assert rule.rule_text, "rule_text不能为空"
            assert rule.complexity in ["basic", "intermediate", "advanced"], "complexity无效"

            # 列表字段检查
            assert isinstance(rule.keywords, list), "keywords必须是列表"
            assert isinstance(rule.related_rules, list), "related_rules必须是列表"

        print("[OK] 数据完整性通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 测试6: API Schema（如果可用）
    print("\n[测试6] API Schema...")
    try:
        from app.presentation.schemas.rule_schemas import (
            RuleQueryRequest,
            RuleCard,
        )

        # 测试请求模型
        req = RuleQueryRequest(query="测试", game="Test Game", top_k=5)
        assert req.query == "测试", "请求模型错误"

        # 测试响应模型
        card = RuleCard(
            rule_id="test-1",
            game="Test",
            version="v1",
            section="1.1",
            rule_text="Test",
            keywords=[],
            complexity="basic",
            source_language="zh-CN",
        )
        assert card.rule_id == "test-1", "响应模型错误"

        print("[OK] API Schema通过")
        passed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        failed += 1

    # 总结
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过 / {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("\n✓ 所有测试通过！项目可以验收。")
        print("\n下一步:")
        print("  1. 启动简单服务器: python simple_server.py")
        print("  2. 测试API: curl http://127.0.0.1:8000/api/rules/mtg-cr-117")
        print("  3. 查看文档: http://127.0.0.1:8000/docs")
        return 0
    else:
        print(f"\n✗ {failed} 个测试失败，请检查。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_end_to_end())
    sys.exit(exit_code)
