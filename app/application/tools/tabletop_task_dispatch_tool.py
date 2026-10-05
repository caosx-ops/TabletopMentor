# -*- coding: utf-8 -*-
"""桌游专用子 Agent 派发工具，隔离电商商品和订单语义。"""
import json
import time
from datetime import datetime, timezone
from typing import Literal

from agentscope.message import TextBlock, ToolResultState, UserMsg
from agentscope.tool import ToolChunk


def build_tabletop_task_dispatch_tool(search_factory, judge_factory, bus):
    async def dispatch_one(subagent_type: str, demands: str) -> dict:
        if subagent_type == "rule_search_agent":
            worker = search_factory.build()
        elif subagent_type == "judge_agent":
            worker = judge_factory.build()
        else:
            return {"agent": subagent_type, "status": "error", "error": "未知桌游子 Agent"}
        started = time.monotonic()
        bus.publish("tabletop", "agent.dispatch", {
            "agent": subagent_type, "demands": demands,
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        try:
            reply = await worker.reply([UserMsg("rule_advisor", demands)])
            result = {"agent": subagent_type, "status": "completed", "summary": reply.get_text_content() or ""}
        except Exception as exc:  # noqa: BLE001
            result = {"agent": subagent_type, "status": "error", "error": type(exc).__name__}
        result["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        bus.publish("tabletop", "tool.result", {"tool": "tabletop_task_dispatch", "agent": subagent_type})
        return result

    async def tabletop_task_dispatch(
        subagent_type: Literal["rule_search_agent", "judge_agent"], demands: str,
    ) -> ToolChunk:
        result = await dispatch_one(subagent_type, demands)
        return ToolChunk(
            content=[TextBlock(text=json.dumps(result, ensure_ascii=False))],
            state=ToolResultState.SUCCESS if result["status"] == "completed" else ToolResultState.ERROR,
        )

    return tabletop_task_dispatch
