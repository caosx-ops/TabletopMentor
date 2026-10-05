# -*- coding: utf-8 -*-
"""集成测试 - 验证改造后的核心流程（不依赖 AgentScope）"""
import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_integration():
    """测试核心集成流程"""
    print("=" * 60)
    print("TabletopMentor 集成测试")
    print("=" * 60)

    # 1. 测试依赖注入配置
    print("\n[1/5] 测试依赖注入配置...")
    try:
        from app.composition import Container
        from app.infrastructure.persistence.in_memory_rule_repository import InMemoryRuleRepository

        rule_repo = InMemoryRuleRepository()
        print(f"[OK] RuleRepository 创建成功")
        print(f"     已加载 {len(await rule_repo.list_all())} 条规则")
    except Exception as e:
        print(f"[FAIL] 依赖注入失败: {e}")
        return

    # 2. 测试规则检索用例
    print("\n[2/5] 测试规则检索用例...")
    try:
        from app.application.usecases.rule_search import RuleSearchUseCase

        search_use_case = RuleSearchUseCase(rule_repo)

        # 测试按ID查询
        rule = await search_use_case.search_by_id("mtg-cr-117")
        assert rule is not None, "规则查询失败"
        print(f"[OK] 按ID查询: {rule.rule_id}")

        # 测试语义检索
        results = await search_use_case.search(query="优先权", top_k=3)
        assert len(results) > 0, "语义检索失败"
        print(f"[OK] 语义检索: 找到 {len(results)} 条规则")

        # 测试游戏过滤
        mtg_rules = await search_use_case.search(
            query="战斗",
            filters={"game": "Magic: The Gathering"}
        )
        print(f"[OK] 游戏过滤: 万智牌规则 {len(mtg_rules)} 条")

    except Exception as e:
        print(f"[FAIL] 检索用例失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. 测试工具函数（不依赖 AgentScope FunctionTool）
    print("\n[3/5] 测试工具函数逻辑...")
    try:
        # 直接测试工具的核心逻辑
        query_result = await search_use_case.search(query="先攻", top_k=5)

        # 模拟工具返回格式
        tool_output = {
            "hits": [
                {
                    "rule_id": r.rule_id,
                    "game": r.game,
                    "section": r.section,
                    "rule_text": r.rule_text,
                    "keywords": r.keywords,
                }
                for r in query_result
            ],
            "total": len(query_result),
        }

        print(f"[OK] 工具逻辑验证")
        print(f"     返回格式: {list(tool_output.keys())}")
        print(f"     命中规则: {tool_output['total']} 条")

    except Exception as e:
        print(f"[FAIL] 工具逻辑失败: {e}")
        return

    # 4. 测试数据完整性
    print("\n[4/5] 测试数据完整性...")
    try:
        all_rules = await rule_repo.list_all()
        games = {}
        for rule in all_rules:
            games[rule.game] = games.get(rule.game, 0) + 1

        print(f"[OK] 数据完整性验证")
        for game, count in games.items():
            print(f"     {game}: {count} 条")

        # 验证关键字段
        for rule in all_rules[:3]:
            assert rule.rule_id, "rule_id 不能为空"
            assert rule.game, "game 不能为空"
            assert rule.rule_text, "rule_text 不能为空"
            assert rule.complexity in ["basic", "intermediate", "advanced"], "complexity 值无效"

        print(f"[OK] 字段验证通过")

    except Exception as e:
        print(f"[FAIL] 数据完整性失败: {e}")
        return

    # 5. 测试多场景查询
    print("\n[5/5] 测试多场景查询...")
    try:
        scenarios = [
            {"query": "优先权", "game": "Magic: The Gathering", "expected_min": 1},
            {"query": "先攻", "game": "D&D 5e", "expected_min": 1},
            {"query": "动作", "game": "D&D 5e", "expected_min": 1},
            {"query": "反应", "game": "Arkham Horror LCG", "expected_min": 1},
        ]

        for scenario in scenarios:
            results = await search_use_case.search(
                query=scenario["query"],
                filters={"game": scenario["game"]}
            )
            assert len(results) >= scenario["expected_min"], \
                f"场景失败: {scenario['query']} in {scenario['game']}"
            print(f"[OK] {scenario['game'][:15]:15} - {scenario['query']:10} : {len(results)} 条")

    except Exception as e:
        print(f"[FAIL] 多场景查询失败: {e}")
        return

    print("\n" + "=" * 60)
    print("[SUCCESS] 所有集成测试通过!")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 安装依赖: uv sync --frozen")
    print("  2. 启动后端: uv run python -m uvicorn app.presentation.server:app")
    print("  3. 启动前端: npm --prefix frontend run dev")


if __name__ == "__main__":
    asyncio.run(test_integration())
