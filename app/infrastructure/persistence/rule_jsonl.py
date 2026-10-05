# -*- coding: utf-8 -*-
"""从授权的 JSONL 规则文件加载桌游规则。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.domain.rules.rule import Rule
from app.domain.rules.rule_variant import RuleVariant


def load_rule_jsonl(path: str | Path) -> list[Rule]:
    rules: list[Rule] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            item: dict[str, Any] = json.loads(raw)
            rule_id = str(item["rule_id"])
            if rule_id in seen:
                raise ValueError(f"重复 rule_id: {rule_id}")
            variants = [RuleVariant(**variant) for variant in item.pop("variants", [])]
            rules.append(Rule(variants=variants, **item))
            seen.add(rule_id)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"规则 JSONL 第 {line_no} 行无效: {exc}") from exc
    if not rules:
        raise ValueError("规则 JSONL 未包含任何规则")
    return rules
