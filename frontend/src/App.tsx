import { FormEvent, useEffect, useState } from "react";
import type { Judgement, RuleCard } from "./types";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const games = ["全部游戏", "Magic: The Gathering", "D&D 5e", "Arkham Horror LCG"];
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) throw new Error((await response.text()) || `请求失败（${response.status}）`);
  return response.json() as Promise<T>;
}
export default function App() {
  const [query, setQuery] = useState("优先权"), [game, setGame] = useState(games[0]);
  const [rules, setRules] = useState<RuleCard[]>([]), [judgements, setJudgements] = useState<Judgement[]>([]);
  const [selected, setSelected] = useState<RuleCard | null>(null), [scenario, setScenario] = useState(""), [ruling, setRuling] = useState("");
  const [message, setMessage] = useState(""), [loading, setLoading] = useState(false);
  const search = async (event?: FormEvent) => {
    event?.preventDefault(); if (!query.trim()) return; setLoading(true); setMessage("");
    try { const data = await request<{ hits: RuleCard[] }>("/api/rules/query", { method: "POST", body: JSON.stringify({ query, game: game === games[0] ? undefined : game, top_k: 8 }) }); setRules(data.hits); }
    catch (error) { setMessage(error instanceof Error ? error.message : "查询失败"); } finally { setLoading(false); }
  };
  const loadJudgements = async () => { try { setJudgements((await request<{ judgements: Judgement[] }>("/api/rules/judgements")).judgements); } catch { /* 后端未启动时不阻塞规则检索 */ } };
  useEffect(() => { void search(); void loadJudgements(); }, []);
  const saveJudgement = async (event: FormEvent) => {
    event.preventDefault(); if (!scenario.trim() || !ruling.trim()) return;
    try { await request("/api/rules/judgement", { method: "POST", body: JSON.stringify({ game: selected?.game ?? (game === games[0] ? "未指定" : game), scenario, ruling, confidence: 0.8, related_rules: selected ? [selected.rule_id] : [] }) }); setScenario(""); setRuling(""); setMessage("裁定已创建，等待确认"); await loadJudgements(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "保存失败"); }
  };
  const decideJudgement = async (id: string, approved: boolean) => {
    try { await request(`/api/rules/judgement/${encodeURIComponent(id)}/decision`, { method: "POST", body: JSON.stringify({ approved }) }); setMessage(approved ? "裁定已批准" : "裁定已拒绝"); await loadJudgements(); }
    catch (error) { setMessage(error instanceof Error ? error.message : "审批失败"); }
  };
  return <div className="tabletop-app">
    <header className="tabletop-header"><div><span className="eyebrow">TABLETOPMENTOR</span><h1>桌游规则顾问</h1><p>查规则、看依据，把桌面争议变成清晰裁定。</p></div><span className="status-dot">本地规则库</span></header>
    <main className="tabletop-main"><section className="query-panel"><form onSubmit={search}><label htmlFor="query">你想确认什么？</label><div className="query-row"><input id="query" value={query} onChange={e => setQuery(e.target.value)} placeholder="例如：对手施放瞬间时我能响应吗？" /><select value={game} onChange={e => setGame(e.target.value)} aria-label="选择游戏">{games.map(item => <option key={item}>{item}</option>)}</select><button type="submit" disabled={loading}>{loading ? "检索中…" : "查询规则"}</button></div></form>{message && <p className="notice" role="status">{message}</p>}</section>
      <section className="content-grid"><div><div className="section-title"><h2>相关规则</h2><span>{rules.length} 条结果</span></div>{rules.length === 0 ? <p className="empty">输入问题开始检索规则。</p> : <div className="rule-list">{rules.map(rule => <article className="rule-card" key={rule.rule_id} onClick={() => { setSelected(rule); setScenario(rule.examples[0] ?? ""); }}><div className="rule-meta"><span>{rule.game}</span><span>{rule.section}</span><span>{rule.complexity}</span></div><h3>{rule.rule_text}</h3><p>{rule.common_mistakes[0] ?? "暂无常见误区"}</p><button type="button" onClick={() => setSelected(rule)}>查看依据与示例 →</button></article>)}</div>}</div>
        <aside className="judgement-panel"><div className="section-title"><h2>裁定记录</h2><span>{judgements.length}</span></div><form onSubmit={saveJudgement}><textarea value={scenario} onChange={e => setScenario(e.target.value)} placeholder="场景：发生了什么？" rows={3} /><textarea value={ruling} onChange={e => setRuling(e.target.value)} placeholder="裁定：依据规则如何处理？" rows={3} /><button type="submit">创建裁定</button></form>{judgements.slice(0, 3).map(item => <div className="judgement-item" key={item.judgement_id}><strong>{item.game}</strong><span className={`judgement-status ${item.status ?? (item.approved ? "approved" : "pending")}`}>{item.status ?? (item.approved ? "approved" : "pending")}</span><p>{item.ruling}</p>{(item.status === "pending" || (!item.status && !item.approved)) && <div className="judgement-actions"><button type="button" onClick={() => void decideJudgement(item.judgement_id, true)}>批准</button><button type="button" onClick={() => void decideJudgement(item.judgement_id, false)}>拒绝</button></div>}</div>)}</aside></section></main>
    {selected && <div className="modal-backdrop" role="presentation" onClick={() => setSelected(null)}><div className="rule-detail" role="dialog" aria-modal="true" onClick={e => e.stopPropagation()}><button className="close" onClick={() => setSelected(null)} aria-label="关闭">×</button><span className="eyebrow">{selected.game} · {selected.section}</span><h2>{selected.rule_text}</h2><p>{selected.examples.join(" ")}</p><h3>关键术语</h3><p>{selected.keywords.join(" · ")}</p><h3>关联规则</h3><p>{selected.related_rules.join(" · ") || "暂无"}</p><button onClick={() => { setScenario(selected.examples[0] ?? ""); setSelected(null); }}>用这条规则创建裁定</button></div></div>}
  </div>;
}
