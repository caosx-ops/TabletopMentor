# -*- coding: utf-8 -*-
"""规则 API Schema 定义"""
from typing import Optional
from pydantic import BaseModel, Field


class RuleQueryRequest(BaseModel):
    """规则查询请求"""
    query: str = Field(..., description="查询文本")
    game: Optional[str] = Field(None, description="游戏名称过滤")
    complexity: Optional[str] = Field(None, description="复杂度过滤: basic/intermediate/advanced")
    top_k: int = Field(5, description="返回数量", ge=1, le=20)


class RuleCard(BaseModel):
    """规则卡片"""
    rule_id: str
    game: str
    version: str
    section: str
    rule_text: str
    keywords: list[str]
    complexity: str
    source_language: str
    translations: dict[str, str] = {}
    related_rules: list[str] = []
    common_mistakes: list[str] = []
    examples: list[str] = []
    source_url: Optional[str] = None
    updated_at: Optional[str] = None
    variants: list[dict] = []


class RuleQueryResponse(BaseModel):
    """规则查询响应"""
    hits: list[RuleCard]
    total: int
    query_normalized: str
    filters_applied: dict = {}


class AgentRuleQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="玩家自然语言问题")
    session_id: str = Field("tabletop-demo", min_length=1)
    user_id: str = Field("api", min_length=1)
    locale: str = "zh-CN"
    currency: str = "CNY"


class AgentRuleQueryResponse(BaseModel):
    session_id: str
    final_text: str
    error: Optional[str] = None


class RuleVersionSnapshot(BaseModel):
    variant_id: str = "current"
    version: str
    rule_text: str
    effective_date: str = ""
    deprecated: bool = False


class RuleVersionCompareRequest(BaseModel):
    from_version: str
    to_version: str


class JudgementRequest(BaseModel):
    """裁定创建请求"""
    user_id: str = Field("api", min_length=1, description="用户标识；MVP 默认演示用户 api")
    game: str
    scenario: str
    ruling: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    related_rules: list[str] = []
    notes: str = ""

class JudgementDecision(BaseModel):
    approved: bool


class JudgementResponse(BaseModel):
    """裁定响应"""
    judgement_id: str
    game: str
    scenario: str
    ruling: str
    confidence: float
    related_rules: list[str]
    notes: str
    status: str
    message: str
