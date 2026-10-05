import { memo, useState, useEffect } from "react";
import type { Judgement } from "../types";
import Icon from "./Icon";
import JudgementCards from "./JudgementCards";

interface JudgementHistoryProps {
  userId: string;
  onViewDetail: (judgement: Judgement) => void;
}

function JudgementHistory({ userId, onViewDetail }: JudgementHistoryProps) {
  const [judgements, setJudgements] = useState<Judgement[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "approved" | "pending">("all");
  const [gameFilter, setGameFilter] = useState<string>("all");

  useEffect(() => {
    loadJudgements();
  }, [userId]);

  const loadJudgements = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/judgements?user_id=${userId}`);
      const data = await response.json();
      setJudgements(data.judgements || []);
    } catch (error) {
      console.error("加载裁定历史失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredJudgements = judgements.filter((j) => {
    if (filter === "approved" && !j.approved) return false;
    if (filter === "pending" && j.approved) return false;
    if (gameFilter !== "all" && j.game !== gameFilter) return false;
    return true;
  });

  const games = Array.from(new Set(judgements.map((j) => j.game)));

  if (loading) {
    return (
      <div className="judgement-history loading">
        <Icon name="loader" />
        <p>加载裁定历史...</p>
      </div>
    );
  }

  return (
    <div className="judgement-history">
      <div className="history-header">
        <h2>
          <Icon name="history" />
          裁定历史
        </h2>

        <div className="filters">
          <select
            value={filter}
            onChange={(e) =>
              setFilter(e.target.value as "all" | "approved" | "pending")
            }
            className="filter-select"
          >
            <option value="all">全部裁定</option>
            <option value="approved">已采纳</option>
            <option value="pending">待确认</option>
          </select>

          <select
            value={gameFilter}
            onChange={(e) => setGameFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">所有游戏</option>
            {games.map((game) => (
              <option key={game} value={game}>
                {game}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filteredJudgements.length === 0 ? (
        <div className="empty-state">
          <Icon name="inbox" />
          <p>暂无裁定记录</p>
        </div>
      ) : (
        <JudgementCards
          judgements={filteredJudgements}
          onApprove={async (j) => {
            // 已审批的不再处理
            if (j.approved) return;
            try {
              await fetch(`/api/judgements/${j.judgement_id}/approve`, {
                method: "POST",
              });
              loadJudgements();
            } catch (error) {
              console.error("批准裁定失败:", error);
            }
          }}
          onReject={async (j) => {
            try {
              await fetch(`/api/judgements/${j.judgement_id}/reject`, {
                method: "POST",
              });
              loadJudgements();
            } catch (error) {
              console.error("拒绝裁定失败:", error);
            }
          }}
          onDetail={onViewDetail}
        />
      )}
    </div>
  );
}

export default memo(JudgementHistory);
