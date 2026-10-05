#!/bin/bash
# TabletopMentor 项目交付验收脚本（Linux/macOS）
set -u

echo "============================================"
echo "TabletopMentor 项目交付验收"
echo "============================================"
echo

# 统计交付物
echo "📦 交付物统计:"
echo "  新增Python文件: $(find app/domain/rules app/application/tools app/application/usecases app/infrastructure/persistence -name '*.py' 2>/dev/null | wc -l) 个"
echo "  前端组件: $(find frontend/src/components -name '*Rule*.tsx' -o -name '*Judgement*.tsx' -o -name '*Player*.tsx' 2>/dev/null | wc -l) 个"
echo "  测试脚本: $(find tests -name 'test_*.py' | wc -l) 个"
echo "  文档: $(ls -1 *.md 2>/dev/null | wc -l) 个"
echo "  规则数据: $(cat data/rules-mvp.jsonl 2>/dev/null | wc -l) 条"
echo

# 运行后端核心测试
echo "🧪 核心功能测试:"
python -m pytest -q tests/test_tabletop_acceptance.py
TEST_EXIT=$?
if [ $TEST_EXIT -ne 0 ]; then
    echo "❌ 桌游 API 验收失败"
    exit $TEST_EXIT
fi

echo "  ✅ 桌游 API：健康检查、规则查询、裁定审批、历史查询通过"

echo "  [可选] 前端构建..."
if [ -x "frontend/node_modules/.bin/tsc" ]; then
    npm --prefix frontend run build
    if [ $? -ne 0 ]; then
        echo "❌ 前端构建失败"
        exit 1
    fi
    echo "  ✅ 前端 TypeScript/Vite 构建通过"
else
    echo "  ⚠️ 前端依赖未安装，跳过构建；请先执行 npm --prefix frontend ci"
fi
echo

# 显示项目状态
echo "📊 项目状态:"
echo "  后端桌游 MVP: 已验收"
echo "  前端构建: 以本机依赖状态为准"
echo "  完整官方规则库与向量检索: 未纳入本次 MVP"
echo

# 验收结论
echo "============================================"
echo "✅ 后端验收结论: 通过"
echo "============================================"
echo
echo "📖 详细报告: docs/改动记录/2026-10-04/桌游规则查询与裁定闭环.md"
echo "🚀 启动服务: python -m uvicorn app.presentation.server:app --host 127.0.0.1 --port 8000"
echo
