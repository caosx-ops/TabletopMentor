import { memo, useState } from "react";
import type { RuleCard } from "../types";
import Icon from "./Icon";

export function RuleIcon({
  rule,
  className = "",
}: {
  rule: RuleCard;
  className?: string;
}) {
  // 根据游戏显示不同图标
  const getGameIcon = (game: string) => {
    if (game.includes("Magic")) return "🃏";
    if (game.includes("D&D")) return "🎲";
    if (game.includes("Arkham")) return "🔮";
    return "📖";
  };

  return (
    <div className={`rule-icon ${className}`}>
      <span className="game-emoji">{getGameIcon(rule.game)}</span>
      <span className="complexity-badge">{rule.complexity}</span>
    </div>
  );
}

interface RuleCardsProps {
  rules: RuleCard[];
  favoriteIds: Set<string>;
  comparedIds: Set<string>;
  onFavorite: (rule: RuleCard) => void;
  onCompare: (rule: RuleCard) => void;
  onDetail: (rule: RuleCard) => void;
}

function RuleCards({
  rules,
  favoriteIds,
  comparedIds,
  onFavorite,
  onCompare,
  onDetail,
}: RuleCardsProps) {
  return (
    <div className="rule-grid">
      {rules.map((rule, index) => {
        const saved = favoriteIds.has(rule.rule_id);
        const selected = comparedIds.has(rule.rule_id);

        return (
          <article
            className={`rule-card ${selected ? "selected" : ""}`}
            key={rule.rule_id}
            style={{ animationDelay: `${Math.min(index, 5) * 55}ms` }}
          >
            <div className="rule-visual">
              <button
                className="rule-open"
                onClick={() => onDetail(rule)}
                aria-label={`查看 ${rule.section} 详情`}
              >
                <RuleIcon rule={rule} />
              </button>
              <button
                className={`favorite-btn ${saved ? "active" : ""}`}
                onClick={() => onFavorite(rule)}
                aria-label={saved ? "取消收藏" : "收藏规则"}
                title={saved ? "取消收藏" : "收藏规则"}
              >
                <Icon name={saved ? "heart-filled" : "heart"} />
              </button>
            </div>

            <div className="rule-info">
              <div className="rule-meta">
                <span className="game-name">{rule.game}</span>
                <span className="section-number">{rule.section}</span>
              </div>

              <h3 className="rule-title" onClick={() => onDetail(rule)}>
                {rule.rule_text.substring(0, 100)}
                {rule.rule_text.length > 100 ? "..." : ""}
              </h3>

              {rule.keywords && rule.keywords.length > 0 && (
                <div className="keywords">
                  {rule.keywords.slice(0, 4).map((keyword, i) => (
                    <span key={i} className="keyword-tag">
                      {keyword}
                    </span>
                  ))}
                </div>
              )}

              <div className="rule-details">
                <span className="version" title="规则版本">
                  <Icon name="tag" />
                  {rule.version}
                </span>
                <span className="complexity" title="复杂度">
                  <Icon name="layers" />
                  {rule.complexity === "basic"
                    ? "基础"
                    : rule.complexity === "intermediate"
                    ? "进阶"
                    : "高级"}
                </span>
              </div>

              {rule.common_mistakes && rule.common_mistakes.length > 0 && (
                <div className="common-mistake">
                  <Icon name="alert-circle" />
                  <span>常见误区：{rule.common_mistakes[0]}</span>
                </div>
              )}

              <div className="rule-actions">
                <button
                  className={`compare-btn ${selected ? "active" : ""}`}
                  onClick={() => onCompare(rule)}
                  disabled={!selected && comparedIds.size >= 3}
                >
                  {selected ? "取消对比" : "加入对比"}
                </button>
                <button className="detail-btn" onClick={() => onDetail(rule)}>
                  查看详情
                </button>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}

export default memo(RuleCards);
