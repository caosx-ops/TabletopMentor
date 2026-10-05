import { memo } from "react";
import type { Judgement } from "../types";
import Icon from "./Icon";

interface JudgementCardsProps {
  judgements: Judgement[];
  onApprove: (judgement: Judgement) => void;
  onReject: (judgement: Judgement) => void;
  onDetail: (judgement: Judgement) => void;
}

function JudgementCards({
  judgements,
  onApprove,
  onReject,
  onDetail,
}: JudgementCardsProps) {
  return (
    <div className="judgement-list">
      {judgements.map((judgement) => {
        const confidenceColor =
          judgement.confidence >= 0.9
            ? "high"
            : judgement.confidence >= 0.6
            ? "medium"
            : "low";

        return (
          <article
            className="judgement-card"
            key={judgement.judgement_id}
            data-approved={judgement.approved}
          >
            <div className="judgement-header">
              <div className="game-badge">
                <Icon name="game-controller" />
                <span>{judgement.game}</span>
              </div>
              <div className={`confidence-badge ${confidenceColor}`}>
                置信度: {(judgement.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div className="judgement-body">
              <div className="scenario-section">
                <h4>
                  <Icon name="help-circle" />
                  场景描述
                </h4>
                <p>{judgement.scenario}</p>
              </div>

              <div className="ruling-section">
                <h4>
                  <Icon name="check-circle" />
                  裁定建议
                </h4>
                <p>{judgement.ruling}</p>
              </div>

              {judgement.related_rules.length > 0 && (
                <div className="related-rules-section">
                  <h4>
                    <Icon name="book-open" />
                    引用规则
                  </h4>
                  <div className="rule-refs">
                    {judgement.related_rules.map((ruleId, i) => (
                      <span key={i} className="rule-ref-tag">
                        {ruleId}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {judgement.notes && (
                <div className="notes-section">
                  <h4>
                    <Icon name="message-circle" />
                    备注
                  </h4>
                  <p>{judgement.notes}</p>
                </div>
              )}
            </div>

            <div className="judgement-actions">
              {!judgement.approved && (
                <>
                  <button
                    className="approve-btn primary"
                    onClick={() => onApprove(judgement)}
                  >
                    <Icon name="check" />
                    确认采纳
                  </button>
                  <button
                    className="reject-btn"
                    onClick={() => onReject(judgement)}
                  >
                    <Icon name="x" />
                    拒绝
                  </button>
                </>
              )}
              <button
                className="detail-btn"
                onClick={() => onDetail(judgement)}
              >
                <Icon name="eye" />
                查看详情
              </button>
            </div>

            <div className="judgement-footer">
              <span className="timestamp">
                {new Date(judgement.created_at).toLocaleString("zh-CN")}
              </span>
              {judgement.approved && (
                <span className="approved-badge">
                  <Icon name="check-circle" />
                  已采纳
                </span>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}

export default memo(JudgementCards);
