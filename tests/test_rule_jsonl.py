import json

from app.infrastructure.persistence.rule_jsonl import load_rule_jsonl


def test_load_authorized_rule_jsonl(tmp_path):
    path = tmp_path / "rules.jsonl"
    path.write_text(json.dumps({
        "rule_id": "demo-1", "game": "Demo", "version": "2025", "section": "1",
        "rule_text": "文本", "keywords": ["示例"], "variants": [{
            "variant_id": "demo-1-old", "version": "2024", "rule_text": "旧文本",
        }],
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    rules = load_rule_jsonl(path)
    assert rules[0].rule_id == "demo-1"
    assert rules[0].variants[0].version == "2024"
