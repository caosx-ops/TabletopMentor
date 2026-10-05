#!/bin/bash
# TabletopMentor 快速验证脚本

echo "======================================"
echo "TabletopMentor 项目验证"
echo "======================================"
echo

# 1. 测试领域模型
echo "[1/3] 测试领域模型..."
python -m tests.test_domain
if [ $? -eq 0 ]; then
    echo "✅ 领域模型测试通过"
else
    echo "❌ 领域模型测试失败"
    exit 1
fi
echo

# 2. 测试规则检索
echo "[2/3] 测试规则检索..."
python -m tests.test_rule_search
if [ $? -eq 0 ]; then
    echo "✅ 规则检索测试通过"
else
    echo "❌ 规则检索测试失败"
    exit 1
fi
echo

# 3. 显示项目统计
echo "[3/3] 项目统计..."
echo "  规则数据: $(cat data/rules-mvp.jsonl | wc -l) 条"
echo "  Python文件: $(find app/domain/rules app/application/tools app/application/usecases -name '*.py' 2>/dev/null | wc -l) 个"
echo "  React组件: $(find frontend/src/components -name '*Rule*.tsx' -o -name '*Judgement*.tsx' -o -name '*Player*.tsx' 2>/dev/null | wc -l) 个"
echo "  测试脚本: $(find tests -name 'test_*.py' | wc -l) 个"
echo

echo "======================================"
echo "✅ 所有验证通过！"
echo "======================================"
echo
echo "下一步:"
echo "  1. 查看完整报告: cat PROJECT_DELIVERY.md"
echo "  2. 安装依赖: uv sync --frozen"
echo "  3. 启动服务: uv run python -m uvicorn app.presentation.server:app"
