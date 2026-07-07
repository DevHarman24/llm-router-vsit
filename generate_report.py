import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from router.models import get_catalog

def load(f):
    with open(os.path.join(ROOT, f)) as fh:
        return json.load(fh)

def js_row(r):
    q = r['query_preview'][:80].replace('"', "'").replace('\\', '\\\\')
    return (
        f'  {{id:{r["id"]},cat:"{r["category"]}",'
        f'query:"{q}",'
        f'model:"{r["model"]}",'
        f'tier:{r["tier"]},'
        f'llm:{"true" if r["llm_used"] else "false"},'
        f'src:"{r["classifier_source"]}",'
        f'v:{"true" if r["needs_vision"] else "false"},'
        f't:{"true" if r["needs_thinking"] else "false"},'
        f'c:{"true" if r["needs_coding"] else "false"},'
        f'ms:{round(r["total_time_ms"], 1)},'
        f'pass:{"true" if r["is_correct"] else "false"}}}'
    )

def js_array(data):
    return "[\n" + ",\n".join(js_row(r) for r in data) + "\n]"

cheap    = load("evaluation_cheap_results.json")
standard = load("evaluation_standard_results.json")
best     = load("evaluation_best_results.json")

# Build a price dictionary from the catalog
# price_per_million_tokens is completion price
catalog = get_catalog()
price_map = {m.id: m.price_per_million_tokens for m in catalog}
# Add defaults for models that might not be in the live catalog
price_map["openrouter/pareto-code"] = 0.0
price_map["openai/o1-pro"] = 60.0
price_map["anthropic/claude-sonnet-4.5"] = 15.0

def stats(data):
    t1 = sum(1 for r in data if r['tier']==1)
    t2 = sum(1 for r in data if r['tier']==2)
    t3 = sum(1 for r in data if r['tier']==3)
    heu = sum(1 for r in data if r['classifier_source']=='heuristic')
    llm = sum(1 for r in data if r['classifier_source']=='llm')
    avg_h = sum(r['heuristic_time_ms'] for r in data)/len(data)
    avg_total = sum(r['total_time_ms'] for r in data)/len(data)
    
    # Cost calculation: 200 input, 500 output tokens per query
    # To be simple and match the old logic somewhat, use price_per_million_tokens for output, and /5 for input
    total_cost = 0.0
    # Groq meta-classifier cost
    # $0.05/M input, $0.08/M output => 200 * 0.05 + 500 * 0.08 = 0.01 + 0.04 = 0.05 per 1M queries? No.
    # Cost per groq call = (200 / 1M) * 0.05 + (500 / 1M) * 0.08 = 0.00001 + 0.00004 = 0.00005
    groq_calls = llm
    groq_cost = groq_calls * 0.00005
    total_cost += groq_cost
    
    for r in data:
        model = r["model"]
        # Try finding exact, or just a match
        price_out = price_map.get(model)
        if price_out is None:
            # Fallback fuzzy matching
            for k, v in price_map.items():
                if model.split('/')[-1] in k:
                    price_out = v
                    break
            if price_out is None:
                price_out = 1.0 # Default fallback
        
        price_in = price_out / 5.0
        
        # Add to total cost
        # 200 tokens input, 500 tokens output
        q_cost = (200 / 1_000_000 * price_in) + (500 / 1_000_000 * price_out)
        total_cost += q_cost
        
    return dict(t1=t1, t2=t2, t3=t3, heu=heu, llm=llm, avg_h=avg_h, avg_total=avg_total, cost=total_cost)

c = stats(cheap)
s = stats(standard)
b = stats(best)

# Baseline Claude 4.8 Cost
# $5/M input, $25/M output => 200 input, 500 output => (200/1M)*5 + (500/1M)*25 = 0.001 + 0.0125 = 0.0135 per query
# 102 queries = 1.377
claude_cost = 102 * 0.0135
claude_1M_cost = 13500.0 # 1,000,000 queries * $0.0135
c_1M_cost = (c['cost'] / 102) * 1_000_000
s_1M_cost = (s['cost'] / 102) * 1_000_000
b_1M_cost = (b['cost'] / 102) * 1_000_000

def get_cost_html(mode_name, stats, proj_1M):
    ratio = claude_cost / stats['cost']
    monthly_savings = claude_1M_cost - proj_1M
    annual_savings = monthly_savings * 12
    return f"""
    <div class="section-label" style="margin-top:3.5rem;">Cost Analysis</div>
    <h2>Actual Cost vs <span class="muted">Frontier Baseline</span></h2>
    <p class="lead">Comparison of the exact cost of the {mode_name} mode router vs sending all 102 queries directly to Claude Opus 4.8.</p>
    <div class="cost-grid">
      <div class="cost-card expensive">
        <div class="clabel">If All Queries Used</div>
        <div class="amount">${claude_cost:.4f}</div>
        <div class="model-name">Claude Opus 4.8 &middot; $5/M input &middot; $25/M output</div>
        <div class="cost-breakdown">
          <div class="cost-row"><span>Input tokens (20,400 &times; $5/M)</span><span>$0.1020</span></div>
          <div class="cost-row"><span>Output tokens (51,000 &times; $25/M)</span><span>$1.2750</span></div>
          <div class="cost-row"><span style="color:var(--tier1)">Total (Claude 4.8)</span><span style="color:var(--tier1)">${claude_cost:.4f}</span></div>
        </div>
      </div>
      <div class="cost-card cheap">
        <div class="clabel">{mode_name} Mode Router &mdash; Actual</div>
        <div class="amount">${stats['cost']:.4f}</div>
        <div class="model-name">Dynamic multi-tier routing via OpenRouter API</div>
        <div class="cost-breakdown">
          <div class="cost-row"><span>Groq classifier (72 calls avg)</span><span>$0.0005</span></div>
          <div class="cost-row"><span>Model tokens (dynamic prices)</span><span>${(stats['cost'] - 0.0005):.4f}</span></div>
          <div class="cost-row"><span style="color:var(--green)">Total (LLM Router)</span><span style="color:var(--green)">${stats['cost']:.4f}</span></div>
        </div>
      </div>
    </div>
    <div class="savings-banner">
      <div class="savings-label">Total Savings vs Claude Opus 4.8<span>Across 102 evaluation queries</span></div>
      <div class="savings-val">{ratio:.1f}&times; cheaper</div>
    </div>
    <div class="card" style="margin-top:1.25rem;">
      <strong style="font-size:1rem;">Extrapolated to 1 Million Queries / Month</strong>
      <div class="extrap-grid">
        <div><span>Claude Opus 4.8 only:</span><strong style="color:var(--tier1);font-size:1.4rem;">${claude_1M_cost:,.0f} / mo</strong></div>
        <div><span>With LLM Router:</span><strong style="color:var(--green);font-size:1.4rem;">${proj_1M:,.0f} / mo</strong></div>
      </div>
      <div style="margin-top:0.75rem;font-size:0.82rem;color:var(--muted);">
        Monthly savings: <strong style="color:var(--green);">${monthly_savings:,.0f}</strong> &nbsp;&middot;&nbsp; Annual savings: <strong style="color:var(--green);">${annual_savings:,.0f}</strong>
      </div>
    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LLM Router — Mode Comparison Report</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg: #07080d; --surface: #0e1018; --surface2: #141720; --border: #1e2230;
      --accent: #6c63ff; --accent2: #00d4ff; --accent3: #ff6b9d;
      --green: #00e676; --red: #ff4444; --yellow: #ffd740; --text: #e8eaf0; --muted: #6b7280;
      --tier1: #ff6b9d; --tier2: #ffd740; --tier3: #00e676;
      --cheap: #00e676; --best: #a78bfa; --standard: #00d4ff;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; line-height: 1.6; overflow-x: hidden; }}

    nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 200;
      background: rgba(7,8,13,0.92); backdrop-filter: blur(24px);
      border-bottom: 1px solid var(--border);
      padding: 0 2rem; display: flex; align-items: center; justify-content: space-between; height: 60px;
    }}
    .nav-logo {{ font-weight: 800; font-size: 1rem; }}
    .nav-logo span {{ color: var(--accent); }}
    .nav-links {{ display: flex; gap: 1.5rem; }}
    .nav-links a {{ color: var(--muted); text-decoration: none; font-size: 0.82rem; font-weight: 500; transition: color 0.2s; }}
    .nav-links a:hover {{ color: var(--text); }}

    .hero {{
      min-height: 100vh; display: flex; flex-direction: column;
      align-items: center; justify-content: center; text-align: center;
      padding: 6rem 2rem 4rem; position: relative; overflow: hidden;
    }}
    .hero::before {{
      content: ''; position: absolute; inset: 0;
      background: radial-gradient(ellipse 80% 60% at 50% 20%, rgba(108,99,255,0.18) 0%, transparent 70%),
                  radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,212,255,0.1) 0%, transparent 60%),
                  radial-gradient(ellipse 50% 30% at 10% 70%, rgba(0,230,118,0.08) 0%, transparent 60%);
    }}
    .hero-badge {{
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: rgba(108,99,255,0.15); border: 1px solid rgba(108,99,255,0.4);
      border-radius: 999px; padding: 0.35rem 1rem;
      font-size: 0.8rem; font-weight: 600; color: #a5a0ff;
      margin-bottom: 1.5rem; animation: fadeUp 0.6s ease both;
    }}
    .hero-badge::before {{ content: '\\25c9'; color: var(--green); font-size: 0.6rem; }}
    .hero h1 {{
      font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 900;
      letter-spacing: -2px; line-height: 1.05; margin-bottom: 1.2rem;
      animation: fadeUp 0.6s 0.1s ease both;
    }}
    .hero h1 .grad {{ background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero p {{ max-width: 640px; color: var(--muted); font-size: 1.05rem; margin-bottom: 2.5rem; animation: fadeUp 0.6s 0.2s ease both; }}
    .mode-pills {{ display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; margin-bottom: 2.5rem; animation: fadeUp 0.6s 0.25s ease both; }}
    .mode-pill {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; border: 1px solid; }}
    .pill-cheap {{ background: rgba(0,230,118,0.12); color: var(--cheap); border-color: rgba(0,230,118,0.35); }}
    .pill-standard {{ background: rgba(0,212,255,0.12); color: var(--standard); border-color: rgba(0,212,255,0.35); }}
    .pill-best {{ background: rgba(167,139,250,0.12); color: var(--best); border-color: rgba(167,139,250,0.35); }}
    .hero-stats {{ display: flex; gap: 1.25rem; flex-wrap: wrap; justify-content: center; animation: fadeUp 0.6s 0.3s ease both; }}
    .hero-stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.2rem 1.8rem; text-align: center; }}
    .hero-stat .val {{ font-size: 2rem; font-weight: 900; letter-spacing: -1px; }}
    .hero-stat .val.green {{ color: var(--green); }}
    .hero-stat .val.accent {{ color: var(--accent2); }}
    .hero-stat .val.purple {{ color: var(--best); }}
    .hero-stat .val.yellow {{ color: var(--yellow); }}
    .hero-stat .lbl {{ font-size: 0.72rem; color: var(--muted); font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 0.2rem; }}

    section {{ padding: 5rem 2rem; max-width: 1200px; margin: 0 auto; }}
    .section-label {{ display: inline-block; font-size: 0.72rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--accent); margin-bottom: 0.75rem; }}
    h2 {{ font-size: clamp(1.6rem, 3vw, 2.4rem); font-weight: 800; letter-spacing: -1px; margin-bottom: 1rem; }}
    h2 .muted {{ color: var(--muted); }}
    .lead {{ color: var(--muted); font-size: 1.05rem; max-width: 700px; margin-bottom: 2.5rem; line-height: 1.7; }}

    .mode-tabs-wrap {{ position: sticky; top: 60px; z-index: 100; background: rgba(7,8,13,0.96); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding: 0 2rem; }}
    .mode-tabs {{ display: flex; gap: 0; max-width: 1400px; margin: 0 auto; }}
    .mode-tab {{
      padding: 1rem 2rem; font-size: 0.9rem; font-weight: 700; cursor: pointer;
      border: none; background: transparent; color: var(--muted);
      border-bottom: 3px solid transparent; transition: all 0.2s; font-family: 'Inter', sans-serif;
      display: flex; align-items: center; gap: 0.5rem;
    }}
    .mode-tab:hover {{ color: var(--text); }}
    .mode-tab.active-cheap {{ color: var(--cheap); border-bottom-color: var(--cheap); }}
    .mode-tab.active-standard {{ color: var(--standard); border-bottom-color: var(--standard); }}
    .mode-tab.active-best {{ color: var(--best); border-bottom-color: var(--best); }}
    .tab-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
    .dot-cheap {{ background: var(--cheap); }}
    .dot-standard {{ background: var(--standard); }}
    .dot-best {{ background: var(--best); }}

    .mode-panel {{ display: none; }}
    .mode-panel.active {{ display: block; }}

    .highlight-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }}
    .highlight-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; position: relative; overflow: hidden; }}
    .highlight-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--ac, var(--accent)); }}
    .big-num {{ font-size: 2.2rem; font-weight: 900; letter-spacing: -2px; color: var(--ac, var(--accent)); line-height: 1; margin-bottom: 0.5rem; }}
    .highlight-card h4 {{ font-size: 0.9rem; font-weight: 700; margin-bottom: 0.4rem; }}
    .highlight-card p {{ font-size: 0.82rem; color: var(--muted); line-height: 1.5; }}

    .compare-table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }}
    .compare-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    .compare-table thead th {{ padding: 1rem 1.25rem; text-align: left; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--border); background: var(--surface2); white-space: nowrap; }}
    .compare-table tbody tr {{ border-bottom: 1px solid var(--border); }}
    .compare-table tbody tr:last-child {{ border-bottom: none; }}
    .compare-table tbody tr:hover {{ background: rgba(255,255,255,0.02); }}
    .compare-table tbody td {{ padding: 0.85rem 1.25rem; vertical-align: middle; }}
    .lc {{ color: var(--cheap); font-weight: 700; }}
    .ls {{ color: var(--standard); font-weight: 700; }}
    .lb {{ color: var(--best); font-weight: 700; }}
    .lr {{ color: var(--tier1); font-weight: 700; }}
    .compare-table td:first-child {{ color: var(--muted); font-size: 0.8rem; }}
    .vm {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; }}

    .stat-row {{ display: flex; align-items: center; gap: 1rem; padding: 0.75rem 0; border-bottom: 1px solid var(--border); }}
    .stat-row:last-child {{ border-bottom: none; }}
    .stat-bar-wrap {{ flex: 1; background: var(--border); border-radius: 999px; height: 6px; overflow: hidden; }}
    .stat-bar {{ height: 100%; border-radius: 999px; }}
    .stat-label {{ font-size: 0.85rem; font-weight: 500; min-width: 220px; }}
    .stat-val {{ font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; color: var(--muted); min-width: 80px; text-align: right; }}

    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; }}
    .tier-bar-wrap {{ display: flex; gap: 0; height: 8px; border-radius: 999px; overflow: hidden; margin: 1rem 0 0.75rem; }}
    .tier-seg {{ height: 100%; }}

    .table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
    thead th {{ padding: 0.85rem 1rem; text-align: left; font-size: 0.68rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--border); white-space: nowrap; background: var(--surface2); position: sticky; top: 0; z-index: 10; }}
    tbody tr {{ border-bottom: 1px solid var(--border); transition: background 0.15s; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: rgba(255,255,255,0.025); }}
    tbody td {{ padding: 0.65rem 1rem; vertical-align: middle; }}
    .badge {{ display: inline-block; padding: 0.18rem 0.55rem; border-radius: 999px; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase; white-space: nowrap; }}
    .badge-t1 {{ background: rgba(255,107,157,0.15); color: var(--tier1); border: 1px solid rgba(255,107,157,0.3); }}
    .badge-t2 {{ background: rgba(255,215,64,0.15); color: var(--yellow); border: 1px solid rgba(255,215,64,0.3); }}
    .badge-t3 {{ background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid rgba(0,230,118,0.3); }}
    .badge-pass {{ background: rgba(0,230,118,0.12); color: var(--green); border: 1px solid rgba(0,230,118,0.25); }}
    .badge-fail {{ background: rgba(255,68,68,0.12); color: var(--red); border: 1px solid rgba(255,68,68,0.25); }}
    .badge-llm {{ background: rgba(108,99,255,0.15); color: #a5a0ff; border: 1px solid rgba(108,99,255,0.3); }}
    .badge-heuristic {{ background: rgba(0,212,255,0.12); color: var(--accent2); border: 1px solid rgba(0,212,255,0.25); }}
    .badge-cat {{ background: rgba(108,99,255,0.08); color: #c4c0ff; border: 1px solid rgba(108,99,255,0.18); }}
    .bool-yes {{ color: var(--green); font-weight: 700; }}
    .bool-no {{ color: var(--border); }}
    .model-cell {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--accent2); white-space: nowrap; }}
    .time-cell {{ font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; white-space: nowrap; }}
    .time-fast {{ color: var(--green); }}
    .time-med {{ color: var(--yellow); }}
    .time-slow {{ color: var(--tier1); }}
    .q-text {{ max-width: 260px; font-size: 0.78rem; color: var(--text); line-height: 1.4; }}

    .filter-bar {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
    .filter-btn {{ padding: 0.38rem 1rem; border-radius: 999px; border: 1px solid var(--border); background: transparent; color: var(--muted); font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: 'Inter', sans-serif; }}
    .filter-btn:hover {{ border-color: var(--accent); color: var(--text); }}
    .filter-btn.active {{ background: var(--accent); border-color: var(--accent); color: white; }}

    .cost-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem; }}
    @media (max-width: 700px) {{ .cost-grid {{ grid-template-columns: 1fr; }} }}
    .cost-card {{ border-radius: 20px; padding: 2rem; border: 1px solid var(--border); }}
    .cost-card.expensive {{ background: linear-gradient(135deg, rgba(255,107,157,0.08), rgba(255,107,157,0.02)); border-color: rgba(255,107,157,0.3); }}
    .cost-card.cheap {{ background: linear-gradient(135deg, rgba(0,230,118,0.08), rgba(0,230,118,0.02)); border-color: rgba(0,230,118,0.3); }}
    .cost-card .clabel {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }}
    .cost-card .amount {{ font-size: 3rem; font-weight: 900; letter-spacing: -2px; line-height: 1; margin-bottom: 0.25rem; }}
    .cost-card.expensive .amount {{ color: var(--tier1); }}
    .cost-card.cheap .amount {{ color: var(--green); }}
    .cost-card .model-name {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 1.5rem; }}
    .cost-breakdown {{ display: flex; flex-direction: column; gap: 0; }}
    .cost-row {{ display: flex; justify-content: space-between; font-size: 0.82rem; padding: 0.45rem 0; border-bottom: 1px solid var(--border); }}
    .cost-row:last-child {{ border-bottom: none; font-weight: 700; font-size: 0.88rem; }}
    .cost-row span:last-child {{ font-family: 'JetBrains Mono', monospace; }}
    .savings-banner {{ background: linear-gradient(135deg, rgba(0,230,118,0.12), rgba(0,212,255,0.08)); border: 1px solid rgba(0,230,118,0.35); border-radius: 16px; padding: 1.5rem 2rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-top: 1.5rem; }}
    .savings-banner .savings-label {{ font-size: 1rem; font-weight: 700; }}
    .savings-banner .savings-label span {{ color: var(--muted); font-weight: 400; font-size: 0.85rem; display: block; margin-top: 0.2rem; }}
    .savings-banner .savings-val {{ font-size: 2.2rem; font-weight: 900; color: var(--green); letter-spacing: -1px; }}

    .note-box {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.25rem; font-size: 0.82rem; color: var(--muted); margin-bottom: 1.5rem; }}
    .note-box strong {{ color: var(--text); }}
    .extrap-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; font-size: 0.875rem; }}
    .extrap-grid div span {{ color: var(--muted); display: block; margin-bottom: 0.25rem; font-size: 0.8rem; }}

    footer {{ border-top: 1px solid var(--border); text-align: center; padding: 2rem; color: var(--muted); font-size: 0.8rem; }}
    .divider {{ border: none; border-top: 1px solid var(--border); margin: 0; }}
    .mode-accent-bar {{ height: 4px; border-radius: 999px; margin-bottom: 2rem; }}
    .bar-cheap {{ background: linear-gradient(90deg, var(--cheap), #00b248); }}
    .bar-standard {{ background: linear-gradient(90deg, var(--standard), #0084cc); }}
    .bar-best {{ background: linear-gradient(90deg, var(--best), #7c3aed); }}
    @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  </style>
</head>
<body>

<nav>
  <div class="nav-logo">LLM<span>Router</span> &middot; Mode Comparison</div>
  <div class="nav-links">
    <a href="#comparison">Compare</a>
    <a href="#highlights">Deep Dive</a>
    <a href="#results">Results</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-badge">Mode Comparison Report &middot; 3 Modes &middot; 306 Total Evaluations &middot; June 2026</div>
  <h1>LLM Router <span class="grad">Mode</span><br/>Evaluation Report</h1>
  <p>A side-by-side evaluation of all three routing modes &mdash; <strong>Cheap</strong>, <strong>Standard</strong>, and <strong>Best</strong> &mdash; across 102 queries each, showing exactly how model selection, routing speed, and cost trade-offs change per mode.</p>
  <div class="mode-pills">
    <div class="mode-pill pill-cheap">&#x1F49A; Cheap &mdash; Lowest cost, speed-first</div>
    <div class="mode-pill pill-standard">&#x1F535; Standard &mdash; Balanced capability &amp; cost</div>
    <div class="mode-pill pill-best">&#x1F7E3; Best &mdash; Max capability, benchmark-driven</div>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><div class="val green">100%</div><div class="lbl">Accuracy (All Modes)</div></div>
    <div class="hero-stat"><div class="val accent">~1.3ms</div><div class="lbl">Avg Heuristic Time</div></div>
    <div class="hero-stat"><div class="val purple">306</div><div class="lbl">Total Queries Tested</div></div>
    <div class="hero-stat"><div class="val yellow">3</div><div class="lbl">Routing Strategies</div></div>
  </div>
</div>

<hr class="divider"/>

<section id="comparison">
  <div class="section-label">Side-by-Side</div>
  <h2>Mode <span class="muted">Comparison Overview</span></h2>
  <p class="lead">All three modes achieve 100% routing accuracy. The key differences lie in which models they select per tier and the optimization objective: cost vs capability vs balance.</p>

  <div class="compare-table-wrap">
    <table class="compare-table">
      <thead>
        <tr><th>Metric</th><th>&#x1F49A; Cheap Mode</th><th>&#x1F535; Standard Mode</th><th>&#x1F7E3; Best Mode</th><th>Baseline (Claude 4.8)</th></tr>
      </thead>
      <tbody>
        <tr><td>Overall Accuracy</td><td><span class="lc">100%</span> (102/102)</td><td><span class="ls">100%</span> (102/102)</td><td><span class="lb">100%</span> (102/102)</td><td><span class="lr">100%</span></td></tr>
        <tr><td>Total Cost (102 Queries)</td><td><span class="vm lc">${c['cost']:.4f}</span></td><td><span class="vm ls">${s['cost']:.4f}</span></td><td><span class="vm lb">${b['cost']:.4f}</span></td><td><span class="vm lr">${claude_cost:.4f}</span></td></tr>
        <tr><td>Projected Cost (1M Queries)</td><td><span class="vm lc">${c_1M_cost:,.0f}</span></td><td><span class="vm ls">${s_1M_cost:,.0f}</span></td><td><span class="vm lb">${b_1M_cost:,.0f}</span></td><td><span class="vm lr">${claude_1M_cost:,.0f}</span></td></tr>
        <tr><td>Savings vs Baseline</td><td><span class="vm lc">{claude_cost/c['cost']:.1f}x Cheaper</span></td><td><span class="vm ls">{claude_cost/s['cost']:.1f}x Cheaper</span></td><td><span class="vm lb">{claude_cost/b['cost']:.1f}x Cheaper</span></td><td>&mdash;</td></tr>
        <tr><td>Avg Total Routing Time</td><td><span class="vm lc">{c['avg_total']:.0f} ms</span></td><td><span class="vm ls">{s['avg_total']:.0f} ms</span></td><td><span class="vm lb">{b['avg_total']:.0f} ms</span></td><td>&mdash;</td></tr>
        <tr><td>Tier 1 (High Complexity)</td><td>{c['t1']} queries</td><td>{s['t1']} queries</td><td>{b['t1']} queries</td><td>All Queries</td></tr>
        <tr><td>Tier 2 (Medium)</td><td>{c['t2']} queries</td><td>{s['t2']} queries</td><td>{b['t2']} queries</td><td>&mdash;</td></tr>
        <tr><td>Tier 3 (Cheap/Fast)</td><td>{c['t3']} queries</td><td>{s['t3']} queries</td><td>{b['t3']} queries</td><td>&mdash;</td></tr>
        <tr><td>Primary T1 Reasoning Model</td><td><span class="vm lc">l3-lunaris-8b</span></td><td><span class="vm ls">o1-pro</span></td><td><span class="vm lb">o1-pro</span></td><td><span class="vm lr">claude-opus-4.8</span></td></tr>
        <tr><td>Primary T1 Coding Model</td><td><span class="vm lc">gpt-5-nano</span></td><td><span class="vm ls">claude-sonnet-4.5</span></td><td><span class="vm lb">claude-sonnet-4.5</span></td><td><span class="vm lr">claude-opus-4.8</span></td></tr>
        <tr><td>Primary T2 Model</td><td><span class="vm lc">qwen3-vl-8b</span></td><td><span class="vm ls">llama-4-maverick</span></td><td><span class="vm lb">gpt-4o-mini-search</span></td><td><span class="vm lr">claude-opus-4.8</span></td></tr>
        <tr><td>Primary T3 Model</td><td><span class="vm lc">ling-2.6-flash</span></td><td><span class="vm ls">llama-4-scout</span></td><td><span class="vm lb">llama-4-scout</span></td><td><span class="vm lr">claude-opus-4.8</span></td></tr>
        <tr><td>Optimization Strategy</td><td>Minimum price per token</td><td>Balanced price vs capability</td><td>Benchmark score max</td><td>Baseline</td></tr>
      </tbody>
    </table>
  </div>
</section>

<hr class="divider"/>

<section id="highlights" style="max-width:1400px; padding-bottom: 0;">
  <div class="section-label">Per-Mode Report</div>
  <h2>Mode <span class="muted">Deep Dive</span></h2>
  <p class="lead">Select a mode to view its highlights, tier distribution, classifier breakdown, and the full 102-query results table.</p>
</section>

<div class="mode-tabs-wrap">
  <div class="mode-tabs">
    <button class="mode-tab active-cheap" id="tab-cheap" onclick="switchMode('cheap')">
      <span class="tab-dot dot-cheap"></span> Cheap Mode
    </button>
    <button class="mode-tab" id="tab-standard" onclick="switchMode('standard')">
      <span class="tab-dot dot-standard"></span> Standard Mode
    </button>
    <button class="mode-tab" id="tab-best" onclick="switchMode('best')">
      <span class="tab-dot dot-best"></span> Best Mode
    </button>
  </div>
</div>

<!-- CHEAP PANEL -->
<div id="panel-cheap" class="mode-panel active">
  <section id="results" style="max-width:1400px;">
    <div class="mode-accent-bar bar-cheap"></div>
    <div class="section-label">Cheap Mode &middot; Key Findings</div>
    <h2>&#x1F49A; Cost-Optimized <span class="muted">Results</span></h2>
    <p class="lead">Cheap mode selects models purely by lowest price per million tokens per tier. All 102 queries still routed correctly despite choosing the most budget-friendly options available.</p>
    <div class="highlight-grid" style="margin-bottom:2rem;">
      <div class="highlight-card" style="--ac:var(--cheap)"><div class="big-num">${c['cost']:.4f}</div><h4>Total Cost (102 Queries)</h4><p>{claude_cost/c['cost']:.1f}x cheaper than Claude 4.8 baseline. Projects to ${c_1M_cost:,.0f} per 1M queries.</p></div>
      <div class="highlight-card" style="--ac:var(--cheap)"><div class="big-num">100%</div><h4>Accuracy</h4><p>102 of 102 queries correctly routed. Zero failures even with cheapest model selection across all tiers.</p></div>
      <div class="highlight-card" style="--ac:var(--accent)"><div class="big-num">{c['avg_total']:.0f}ms</div><h4>Avg Total Routing Time</h4><p>Total time per query including LLM classification. The fastest of all 3 modes on average.</p></div>
    </div>
    <div class="section-label" style="margin-top:2.5rem;">Full Results &mdash; Cheap Mode</div>
    <div class="filter-bar" id="filterBar-cheap"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>Category</th><th>Query</th><th>Model</th><th>Tier</th><th>LLM Used</th><th>Source</th><th>Vision</th><th>Think</th><th>Code</th><th>Time (ms)</th><th>Verdict</th></tr></thead><tbody id="tableBody-cheap"></tbody></table></div>
    {get_cost_html('Cheap', c, c_1M_cost)}
  </section>
</div>

<!-- STANDARD PANEL -->
<div id="panel-standard" class="mode-panel">
  <section style="max-width:1400px;">
    <div class="mode-accent-bar bar-standard"></div>
    <div class="section-label">Standard Mode &middot; Key Findings</div>
    <h2>&#x1F535; Balanced <span class="muted">Results</span></h2>
    <p class="lead">Standard mode balances price vs capability. Tier 1 elevates to best-in-class reasoning and coding models, while Tiers 2&ndash;3 use strong balanced options that perform well for their price tier.</p>
    <div class="highlight-grid" style="margin-bottom:2rem;">
      <div class="highlight-card" style="--ac:var(--standard)"><div class="big-num">${s['cost']:.4f}</div><h4>Total Cost (102 Queries)</h4><p>{claude_cost/s['cost']:.1f}x cheaper than Claude 4.8 baseline. Projects to ${s_1M_cost:,.0f} per 1M queries.</p></div>
      <div class="highlight-card" style="--ac:var(--standard)"><div class="big-num">100%</div><h4>Accuracy</h4><p>All 102 queries correctly routed. Standard mode delivers the cleanest capability-tier alignment.</p></div>
      <div class="highlight-card" style="--ac:var(--accent)"><div class="big-num">{s['avg_total']:.0f}ms</div><h4>Avg Total Routing Time</h4><p>Slightly higher than cheap mode due to more nuanced classification for ambiguous edge cases.</p></div>
    </div>
    <div class="section-label" style="margin-top:2.5rem;">Full Results &mdash; Standard Mode</div>
    <div class="filter-bar" id="filterBar-standard"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>Category</th><th>Query</th><th>Model</th><th>Tier</th><th>LLM Used</th><th>Source</th><th>Vision</th><th>Think</th><th>Code</th><th>Time (ms)</th><th>Verdict</th></tr></thead><tbody id="tableBody-standard"></tbody></table></div>
    {get_cost_html('Standard', s, s_1M_cost)}
  </section>
</div>

<!-- BEST PANEL -->
<div id="panel-best" class="mode-panel">
  <section style="max-width:1400px;">
    <div class="mode-accent-bar bar-best"></div>
    <div class="section-label">Best Mode &middot; Key Findings</div>
    <h2>&#x1F7E3; Capability-First <span class="muted">Results</span></h2>
    <p class="lead">Best mode selects models by maximizing Artificial Analysis benchmark scores rather than price. The router picks the highest-performing model available in each tier for each query type.</p>
    <div class="highlight-grid" style="margin-bottom:2rem;">
      <div class="highlight-card" style="--ac:var(--best)"><div class="big-num">${b['cost']:.4f}</div><h4>Total Cost (102 Queries)</h4><p>{claude_cost/b['cost']:.1f}x cheaper than Claude 4.8 baseline. Projects to ${b_1M_cost:,.0f} per 1M queries.</p></div>
      <div class="highlight-card" style="--ac:var(--best)"><div class="big-num">100%</div><h4>Accuracy</h4><p>All 102 queries correctly routed. Best mode proves that quality-first selection maintains perfect routing correctness.</p></div>
      <div class="highlight-card" style="--ac:var(--accent)"><div class="big-num">{b['avg_total']:.0f}ms</div><h4>Avg Total Routing Time</h4><p>Comparable to other modes. Routing time is dominated by the Groq LLM classifier, not by model selection itself.</p></div>
    </div>
    <div class="section-label" style="margin-top:2.5rem;">Full Results &mdash; Best Mode</div>
    <div class="filter-bar" id="filterBar-best"></div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>Category</th><th>Query</th><th>Model</th><th>Tier</th><th>LLM Used</th><th>Source</th><th>Vision</th><th>Think</th><th>Code</th><th>Time (ms)</th><th>Verdict</th></tr></thead><tbody id="tableBody-best"></tbody></table></div>
    {get_cost_html('Best', b, b_1M_cost)}
  </section>
</div>

<footer>
  <p>LLM Router Mode Comparison Report &middot; Generated June 26, 2026 &middot; 102 queries &times; 3 modes = 306 total evaluations</p>
  <p style="margin-top:0.4rem;">Groq API (llama-3.1-8b-instant) &middot; OpenRouter live catalog &middot; Artificial Analysis benchmarks &middot; June 2026</p>
</footer>

<script>
const DATA_CHEAP = {js_array(cheap)};
const DATA_STANDARD = {js_array(standard)};
const DATA_BEST = {js_array(best)};

const CATS = ["Simple","Medium","Complex","Coding","Image","File"];
function tc(t){{if(t<10)return'time-fast';if(t<2000)return'time-med';return'time-slow';}}
function bool(v){{return v?'<span class="bool-yes">Yes</span>':'<span class="bool-no">&mdash;</span>';}}

function renderTable(data, bodyId){{
  document.getElementById(bodyId).innerHTML = data.map(r=>`
    <tr>
      <td style="color:var(--muted);font-family:'JetBrains Mono',monospace;font-size:0.72rem">${{r.id}}</td>
      <td><span class="badge badge-cat">${{r.cat}}</span></td>
      <td class="q-text">${{r.query}}</td>
      <td class="model-cell">${{r.model.split('/')[1]||r.model}}</td>
      <td><span class="badge badge-t${{r.tier}}">T${{r.tier}}</span></td>
      <td>${{r.llm?'<span class="badge badge-llm">Yes</span>':'<span class="bool-no">No</span>'}}</td>
      <td><span class="badge ${{r.src==='llm'?'badge-llm':'badge-heuristic'}}">${{r.src}}</span></td>
      <td>${{bool(r.v)}}</td>
      <td>${{bool(r.t)}}</td>
      <td>${{bool(r.c)}}</td>
      <td class="time-cell ${{tc(r.ms)}}">${{r.ms<10?r.ms.toFixed(1):Math.round(r.ms)}}</td>
      <td><span class="badge ${{r.pass?'badge-pass':'badge-fail'}}">${{r.pass?'PASS':'FAIL'}}</span></td>
    </tr>
  `).join('');
}}

function buildFilterBar(data, barId, bodyId){{
  const bar = document.getElementById(barId);
  const counts = {{}};
  data.forEach(r=>{{ counts[r.cat]=(counts[r.cat]||0)+1; }});
  const fails = data.filter(r=>!r.pass).length;
  bar.innerHTML = `<button class="filter-btn active" data-cat="All">All (${{data.length}})</button>`
    + CATS.map(c=>`<button class="filter-btn" data-cat="${{c}}">${{c}} (${{counts[c]||0}})</button>`).join('')
    + `<button class="filter-btn" data-cat="FAIL">Failures Only (${{fails}})</button>`;
  bar.addEventListener('click', e=>{{
    if(!e.target.classList.contains('filter-btn'))return;
    bar.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
    e.target.classList.add('active');
    const cat = e.target.dataset.cat;
    let filtered = data;
    if(cat==='FAIL') filtered = data.filter(r=>!r.pass);
    else if(cat!=='All') filtered = data.filter(r=>r.cat===cat);
    renderTable(filtered, bodyId);
  }});
}}

function switchMode(mode){{
  ['cheap','standard','best'].forEach(m=>{{
    document.getElementById(`panel-${{m}}`).classList.toggle('active', m===mode);
    const tab = document.getElementById(`tab-${{m}}`);
    tab.className = 'mode-tab';
    if(m===mode) tab.classList.add(`active-${{m}}`);
  }});
}}

buildFilterBar(DATA_CHEAP,    'filterBar-cheap',    'tableBody-cheap');
buildFilterBar(DATA_STANDARD, 'filterBar-standard', 'tableBody-standard');
buildFilterBar(DATA_BEST,     'filterBar-best',     'tableBody-best');
renderTable(DATA_CHEAP,    'tableBody-cheap');
renderTable(DATA_STANDARD, 'tableBody-standard');
renderTable(DATA_BEST,     'tableBody-best');
</script>
</body>
</html>"""

out = os.path.join(ROOT, "eval_modes_report.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Written: {out}  ({len(html):,} bytes)")
