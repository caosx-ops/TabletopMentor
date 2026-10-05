"""桌游模式可验收冒烟测试：完整服务、规则 API、裁定审批。"""
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.presentation.server import app
from app.application.agents.orchestrator import SubmitIntentOutput


def test_tabletop_rule_and_judgement_flow():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        result = client.post("/api/rules/query", json={"query": "优先权", "game": "Magic: The Gathering"})
        assert result.status_code == 200
        assert result.json()["total"] >= 1

        capabilities = client.get("/api/rules/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["retrieval"]["lexical"] == "bm25"

        versions = client.get("/api/rules/mtg-cr-117/versions")
        assert versions.status_code == 200
        assert versions.json()[0]["version"] == "CR 2024-03-08"

        created = client.post("/api/rules/judgement", json={
            "user_id": "acceptance-user", "game": "Magic: The Gathering", "scenario": "对手施放瞬间",
            "ruling": "可以响应", "confidence": 0.9, "related_rules": ["mtg-cr-117"],
        })
        assert created.status_code == 200
        judgement_id = created.json()["judgement_id"]
        assert created.json()["status"] == "pending"

        decision = client.post(f"/api/rules/judgement/{judgement_id}/decision", json={"approved": True})
        assert decision.status_code == 200
        assert decision.json()["status"] == "approved"

        history = client.get("/api/rules/judgements?user_id=acceptance-user")
        assert history.status_code == 200
        assert any(item["judgement_id"] == judgement_id and item["status"] == "approved" for item in history.json()["judgements"])

        # Agent 入口使用真实编排器接口；测试替换模型调用，验证请求协议不依赖外部 LLM。
        orchestrator = client.app.state.container.orchestrator
        original = orchestrator.handle_intent
        orchestrator.handle_intent = AsyncMock(return_value=SubmitIntentOutput(
            shopping_session_id="agent-test", final_text="依据规则可以响应。",
        ))
        try:
            agent_result = client.post("/api/rules/agent/query", json={
                "query": "对手施放瞬间时我能响应吗？", "session_id": "agent-test", "user_id": "api",
            })
            assert agent_result.status_code == 200
            assert agent_result.json()["final_text"] == "依据规则可以响应。"
            orchestrator.handle_intent.assert_awaited_once()
        finally:
            orchestrator.handle_intent = original
