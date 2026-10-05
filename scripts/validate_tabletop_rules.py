"""校验并统计授权规则 JSONL 文件。"""
from __future__ import annotations

import argparse
from collections import Counter

from app.infrastructure.persistence.rule_jsonl import load_rule_jsonl


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="规则 JSONL 路径")
    args = parser.parse_args()
    rules = load_rule_jsonl(args.path)
    games = Counter(rule.game for rule in rules)
    print(f"rules={len(rules)}")
    for game, count in sorted(games.items()):
        print(f"{game}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
