import { memo, useState, useCallback } from "react";
import type { RuleCard, Judgement } from "../types";
import RuleCards from "./RuleCards";
import JudgementHistory from "./JudgementHistory";
import Icon from "./Icon";
import Modal from "./Modal";

interface PlayerWorkspaceProps {
  userId: string;
}

function PlayerWorkspace({ userId }: PlayerWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<"rules" | "judgements">("rules");
  const [favoriteRules, setFavoriteRules] = useState<Set<string>>(new Set());
  const [comparedRules, setComparedRules] = useState<Set<string>>(new Set());
  const [selectedRule, setSelectedRule] = useState<RuleCard | null>(null);
  const [selectedJudgement, setSelectedJudgement] = useState<Judgement | null>(
    null
  );

  const handleFavoriteRule = useCallback((rule: RuleCard) => {
    setFavoriteRules((prev) => {
      const next = new Set(prev);
      if (next.has(rule.rule_id)) {
        next.delete(rule.rule_id);
      } else {
        next.add(rule.rule_id);
      }
      return next;
    });
  }, []);

  const handleCompareRule = useCallback((rule: RuleCard) => {
    setComparedRules((prev) => {
      const next = new Set(prev);
      if (next.has(rule.rule_id)) {
        next.delete(rule.rule_id);
      } else {
        if (next.size >= 3) return prev; // 最多对比3条规则
        next.add(rule.rule_id);
      }
      return next;
    });
  }, []);

  const handleRuleDetail = useCallback((rule: RuleCard) => {
    setSelectedRule(rule);
  }, []);

  const handleJudgementDetail = useCallback((judgement: Judgement) => {
    setSelectedJudgement(judgement);
  }, []);

  return (
    <div className="player-workspace">
      <div className="workspace-header">
        <h1>
          <Icon name="book-open" />
          我的桌游助手
        </h1>

        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === "rules" ? "active" : ""}`}
            onClick={() => setActiveTab("rules")}
          >
            <Icon name="search" />
            规则查询
          </button>
          <button
            className={`tab-btn ${activeTab === "judgements" ? "active" : ""}`}
            onClick={() => setActiveTab("judgements")}
          >
            <Icon name="clipboard" />
            裁定历史
          </button>
        </div>
      </div>

      <div className="workspace-content">
        {activeTab === "rules" && (
          <div className="rules-section">
            <div className="section-info">
              <p>收藏的规则和对比记录</p>
              {comparedRules.size > 0 && (
                <span className="compare-count">
                  已选择 {comparedRules.size}/3 条规则对比
                </span>
              )}
            </div>

            {/* 这里应该加载用户收藏的规则 */}
            <div className="placeholder">
              <Icon name="bookmark" />
              <p>您还没有收藏任何规则</p>
              <small>在对话中查询规则后，点击收藏按钮即可保存</small>
            </div>
          </div>
        )}

        {activeTab === "judgements" && (
          <JudgementHistory
            userId={userId}
            onViewDetail={handleJudgementDetail}
          />
        )}
      </div>

      {/* 规则详情弹窗 */}
      {selectedRule && (
        <Modal
          isOpen={!!selectedRule}
          onClose={() => setSelectedRule(null)}
          title="规则详情"
        >
          <div className="rule-detail-modal">
            <div className="rule-header">
              <span className="game-badge">{selectedRule.game}</span>
              <span className="section-badge">{selectedRule.section}</span>
              <span className="version-badge">{selectedRule.version}</span>
            </div>

            <div className="rule-content">
              <h3>规则正文</h3>
              <p className="rule-text">{selectedRule.rule_text}</p>

              {selectedRule.keywords.length > 0 && (
                <div className="keywords-section">
                  <h4>关键术语</h4>
                  <div className="keyword-tags">
                    {selectedRule.keywords.map((kw, i) => (
                      <span key={i} className="keyword-tag">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedRule.common_mistakes.length > 0 && (
                <div className="mistakes-section">
                  <h4>
                    <Icon name="alert-triangle" />
                    常见误区
                  </h4>
                  <ul>
                    {selectedRule.common_mistakes.map((mistake, i) => (
                      <li key={i}>{mistake}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedRule.examples.length > 0 && (
                <div className="examples-section">
                  <h4>
                    <Icon name="lightbulb" />
                    应用示例
                  </h4>
                  <ul>
                    {selectedRule.examples.map((example, i) => (
                      <li key={i}>{example}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedRule.related_rules.length > 0 && (
                <div className="related-section">
                  <h4>
                    <Icon name="link" />
                    相关规则
                  </h4>
                  <div className="related-tags">
                    {selectedRule.related_rules.map((rid, i) => (
                      <span key={i} className="related-tag">
                        {rid}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedRule.source_url && (
                <div className="source-section">
                  <a
                    href={selectedRule.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Icon name="external-link" />
                    查看官方规则来源
                  </a>
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}

      {/* 裁定详情弹窗 */}
      {selectedJudgement && (
        <Modal
          isOpen={!!selectedJudgement}
          onClose={() => setSelectedJudgement(null)}
          title="裁定详情"
        >
          <div className="judgement-detail-modal">
            <div className="judgement-meta">
              <span className="game-badge">{selectedJudgement.game}</span>
              <span className="confidence-badge">
                置信度: {(selectedJudgement.confidence * 100).toFixed(0)}%
              </span>
            </div>

            <div className="scenario">
              <h4>场景描述</h4>
              <p>{selectedJudgement.scenario}</p>
            </div>

            <div className="ruling">
              <h4>裁定建议</h4>
              <p>{selectedJudgement.ruling}</p>
            </div>

            {selectedJudgement.related_rules.length > 0 && (
              <div className="related-rules">
                <h4>引用规则</h4>
                <div className="rule-refs">
                  {selectedJudgement.related_rules.map((rid, i) => (
                    <span key={i} className="rule-ref-tag">
                      {rid}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedJudgement.notes && (
              <div className="notes">
                <h4>备注</h4>
                <p>{selectedJudgement.notes}</p>
              </div>
            )}

            <div className="timestamp">
              创建时间:{" "}
              {new Date(selectedJudgement.created_at).toLocaleString("zh-CN")}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

export default memo(PlayerWorkspace);
