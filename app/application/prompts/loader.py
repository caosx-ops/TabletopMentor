# -*- coding: utf-8 -*-
"""PromptLoader

读取并缓存 app/application/prompts/globex.yml，全项目提示词只从这里取。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import os

import yaml

PROMPTS_DIR = Path(__file__).resolve().parent


def prompt_path() -> Path:
    """根据运行模式选择领域 Prompt；默认保持旧电商行为兼容。"""
    filename = "tabletop.yml" if os.getenv("TABLETOP_MODE", "0").lower() in {"1", "true", "yes"} else "globex.yml"
    return PROMPTS_DIR / filename


@lru_cache(maxsize=1)
def _load_default_prompts() -> dict:
    with open(prompt_path(), encoding="utf-8") as f:
        document = yaml.safe_load(f)
    if "sub_agents" not in document and "search_agent" in document and "trade_agent" in document:
        document["sub_agents"] = {"search": document.pop("search_agent"), "trade": document.pop("trade_agent")}
    return document


def load_prompts() -> dict:
    from app.infrastructure.context import ShoppingContext
    snapshot = ShoppingContext.current()
    if snapshot is not None and snapshot.prompt_document_json:
        # 每次返回新对象，调用方不能修改不可变版本的共享正文。
        return json.loads(snapshot.prompt_document_json)
    return json.loads(json.dumps(_load_default_prompts(), ensure_ascii=False))


# 保持离线工具与旧测试的清缓存入口。
load_prompts.cache_clear = _load_default_prompts.cache_clear
