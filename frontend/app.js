/* ─────────────────────────────────────────────────────────────────────
   LLM Router — Frontend Logic
   ───────────────────────────────────────────────────────────────────── */

const API_BASE = window.location.origin;

/* ── State ─────────────────────────────────────────────────────────── */
let attachedFiles = [];
let stats = { total: 0, tier1: 0, tier2: 0, tier3: 0, totalMs: 0 };
let isRouting = false;

/* ── DOM refs ──────────────────────────────────────────────────────── */
const queryInput     = document.getElementById('queryInput');
const sendBtn        = document.getElementById('sendBtn');
const fileInput      = document.getElementById('fileInput');
const attachPreview  = document.getElementById('attachmentPreview');
const attachList     = document.getElementById('attachmentList');
const chatWindow     = document.getElementById('chatWindow');
const messages       = document.getElementById('messages');
const emptyState     = document.getElementById('emptyState');
const catalogBtn     = document.getElementById('catalogBtn');
const catalogModal   = document.getElementById('catalogModal');
const modalClose     = document.getElementById('modalClose');
const catalogBody    = document.getElementById('catalogBody');
const catalogSearch  = document.getElementById('catalogSearch');
const newChatBtn     = document.getElementById('newChatBtn');
const mobileToggle   = document.getElementById('mobileToggle');
const sidebarToggle  = document.getElementById('sidebarToggle');
const sidebar        = document.getElementById('sidebar');
const statusDot      = document.getElementById('statusDot');
const statusText     = document.getElementById('statusText');

/* ── Auto-resize textarea ──────────────────────────────────────────── */
queryInput.addEventListener('input', () => {
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 200) + 'px';
});

/* ── Enter to send ─────────────────────────────────────────────────── */
queryInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

sendBtn.addEventListener('click', handleSend);

/* ── File attachment ───────────────────────────────────────────────── */
fileInput.addEventListener('change', (e) => {
  const files = Array.from(e.target.files);
  files.forEach(addAttachment);
  fileInput.value = '';
});

function addAttachment(file) {
  if (attachedFiles.length >= 4) return;
  attachedFiles.push(file);
  renderAttachmentPreviews();
}

function removeAttachment(idx) {
  attachedFiles.splice(idx, 1);
  renderAttachmentPreviews();
}

function renderAttachmentPreviews() {
  attachList.innerHTML = '';
  if (attachedFiles.length === 0) {
    attachPreview.style.display = 'none';
    return;
  }
  attachPreview.style.display = 'block';
  attachedFiles.forEach((file, i) => {
    const isImage = file.type.startsWith('image/');
    const chip = document.createElement('div');
    chip.className = `attachment-chip ${isImage ? 'is-image' : ''}`;

    if (isImage) {
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      chip.appendChild(img);
    } else {
      chip.innerHTML = `<span>📄</span>`;
    }

    const name = document.createElement('span');
    name.textContent = file.name.length > 20 ? file.name.slice(0, 18) + '…' : file.name;
    chip.appendChild(name);

    const rem = document.createElement('button');
    rem.className = 'remove-btn';
    rem.textContent = '×';
    rem.addEventListener('click', () => removeAttachment(i));
    chip.appendChild(rem);

    attachList.appendChild(chip);
  });
}

/* ── Main send handler ─────────────────────────────────────────────── */
async function handleSend() {
  const query = queryInput.value.trim();
  if (!query || isRouting) return;

  isRouting = true;
  sendBtn.disabled = true;

  // Hide empty state
  emptyState.style.display = 'none';

  // Capture current attachments
  const currentFiles = [...attachedFiles];
  const hasImage = currentFiles.some(f => f.type.startsWith('image/'));
  const hasFile  = currentFiles.some(f => !f.type.startsWith('image/'));
  const totalSizeKb = currentFiles.reduce((s, f) => s + f.size / 1024, 0);

  // Build attachment tags for display
  const attachmentHtml = currentFiles.length > 0
    ? currentFiles.map(f => `
        <div class="attachment-tag">
          ${f.type.startsWith('image/') ? '🖼️' : '📄'} ${escapeHtml(f.name)}
        </div>`).join('')
    : '';

  // Render user message
  appendUserMessage(query, attachmentHtml);

  // Clear input
  queryInput.value = '';
  queryInput.style.height = 'auto';
  attachedFiles = [];
  renderAttachmentPreviews();

  // Show loading card
  const loadingId = showLoadingCard();

  try {
    let result;
    if (currentFiles.length > 0) {
      // Use multipart form endpoint
      const formData = new FormData();
      formData.append('query', query);
      formData.append('file', currentFiles[0]); // Primary file
      const resp = await fetch(`${API_BASE}/api/route-with-file`, {
        method: 'POST',
        body: formData
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      result = await resp.json();
    } else {
      // JSON endpoint
      const resp = await fetch(`${API_BASE}/api/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          has_image: false,
          has_file: false,
          file_size_kb: 0
        })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      result = await resp.json();
    }

    removeLoadingCard(loadingId);
    appendRouterCard(result);
    updateStats(result);

  } catch (err) {
    removeLoadingCard(loadingId);
    appendErrorCard(err.message);
  }

  isRouting = false;
  sendBtn.disabled = false;
  queryInput.focus();
  scrollToBottom();
}

/* ── tryExample (called from HTML) ────────────────────────────────── */
function tryExample(text) {
  queryInput.value = text;
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 200) + 'px';
  queryInput.focus();
}

/* ── Render helpers ────────────────────────────────────────────────── */
function appendUserMessage(text, attachHtml) {
  const div = document.createElement('div');
  div.className = 'message-group';
  div.innerHTML = `
    <div class="user-message">
      ${attachHtml}
      ${escapeHtml(text)}
    </div>
  `;
  messages.appendChild(div);
  scrollToBottom();
}

function showLoadingCard() {
  const id = 'loading-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = 'loading-card';
  div.innerHTML = `
    <div class="spinner"></div>
    <span>Routing query<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></span>
  `;
  messages.appendChild(div);
  scrollToBottom();
  return id;
}

function removeLoadingCard(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendRouterCard(result) {
  const tier = result.tier;
  const tierClass = `tier-pill-${tier}`;
  const tierColors = { 1: 'tier1', 2: 'tier2', 3: 'tier3' };
  const tierEmojis = { 1: '🔴', 2: '🟡', 3: '🟢' };
  const tierLabels = { 1: 'Tier 1 · Frontier', 2: 'Tier 2 · Balanced', 3: 'Tier 3 · Efficient' };

  // Format numbers
  const totalMs = result.total_time_ms.toFixed(1);
  const heuristicMs = result.heuristic_time_ms.toFixed(1);
  const llmMs = result.llm_time_ms > 0 ? result.llm_time_ms.toFixed(1) : '—';
  const ctxK = (result.context_window / 1000).toFixed(0) + 'K';
  const price = result.price_per_million_tokens > 0
    ? `$${result.price_per_million_tokens.toFixed(2)}/M tokens`
    : 'Free/Unknown';

  // Capability tags
  const caps = [
    { key: 'Vision',   active: result.needs_vision,   icon: eyeIcon(),     supported: result.supports_vision },
    { key: 'Thinking', active: result.needs_thinking,  icon: brainIcon(),   supported: result.supports_thinking },
    { key: 'Coding',   active: result.needs_coding,    icon: codeIcon(),    supported: result.supports_coding },
  ];

  const capHtml = caps.map(c => `
    <div class="cap-tag ${c.active ? 'active' : ''}">
      ${c.icon} ${c.key}${c.active ? ' ✓' : ''}
    </div>
  `).join('');

  // Signals
  const signalHtml = result.signals.length > 0
    ? result.signals.map(s => `<span class="signal-tag">${escapeHtml(s)}</span>`).join('')
    : '<span class="signal-tag">none</span>';

  // LLM layer badge
  const llmBadge = result.llm_used
    ? `<span class="llm-layer-badge used">⚡ Groq LLM Used</span>`
    : `<span class="llm-layer-badge skipped">Heuristic Only</span>`;

  const div = document.createElement('div');
  div.className = 'message-group';
  div.innerHTML = `
    <div class="router-card">
      <div class="router-card-header">
        <div class="router-avatar">
          ${routerIcon()}
        </div>
        <span class="router-card-label">Router Decision</span>
        ${llmBadge}
      </div>

      <div class="decision-banner">
        <div class="model-badge">
          <div class="model-tier-pill ${tierClass}">
            ${tierEmojis[tier]} ${tierLabels[tier]}
          </div>
          <div class="model-name">${escapeHtml(result.model_name)}</div>
          <div class="model-id">${escapeHtml(result.model_id)}</div>
        </div>
        <div class="timing-display">
          <div class="timing-total">${totalMs}</div>
          <div class="timing-unit">ms decision time</div>
          <div class="timing-breakdown">
            <span class="timing-chip" title="Heuristics time">H: ${heuristicMs}ms</span>
            <span class="timing-chip" title="LLM classifier time">LLM: ${llmMs}ms</span>
          </div>
        </div>
      </div>

      <div class="capability-tags">
        ${capHtml}
      </div>

      <div class="router-details">
        <div class="detail-row">
          <span class="detail-key">Provider</span>
          <span class="detail-val">
            <span class="provider-chip">${escapeHtml(result.provider)}</span>
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-key">Context</span>
          <span class="detail-val mono">${ctxK} tokens</span>
        </div>
        <div class="detail-row">
          <span class="detail-key">Cost</span>
          <span class="detail-val mono">${price}</span>
        </div>
        <div class="detail-row">
          <span class="detail-key">Reasoning</span>
          <span class="detail-val">${escapeHtml(result.reasoning || '—')}</span>
        </div>
        <div class="detail-row">
          <span class="detail-key">Signals</span>
          <span class="detail-val">
            <div class="signal-tags">${signalHtml}</div>
          </span>
        </div>
      </div>
    </div>
  `;
  messages.appendChild(div);
}

function appendErrorCard(msg) {
  const div = document.createElement('div');
  div.className = 'message-group';
  div.innerHTML = `
    <div class="router-card" style="border-color: var(--tier1-border)">
      <div class="router-card-header">
        <span class="router-card-label" style="color:var(--tier1)">⚠ Routing Error</span>
      </div>
      <div class="decision-banner">
        <div class="model-badge">
          <div class="model-name" style="font-size:15px;color:var(--tier1)">Could not reach backend</div>
          <div class="model-id">${escapeHtml(msg)}</div>
        </div>
      </div>
      <div class="router-details">
        <div class="detail-row">
          <span class="detail-key">Fix</span>
          <span class="detail-val">Make sure the FastAPI server is running on port 8000</span>
        </div>
      </div>
    </div>
  `;
  messages.appendChild(div);
}

/* ── Stats ─────────────────────────────────────────────────────────── */
function updateStats(result) {
  stats.total++;
  stats.totalMs += result.total_time_ms;
  if (result.tier === 1) stats.tier1++;
  else if (result.tier === 3) stats.tier3++;

  document.getElementById('statTotal').textContent   = stats.total;
  document.getElementById('statAvgTime').textContent = (stats.totalMs / stats.total).toFixed(0) + 'ms';
  document.getElementById('statTier1').textContent   = stats.tier1;
  document.getElementById('statTier3').textContent   = stats.tier3;
}

/* ── Model Catalog Modal ────────────────────────────────────────────── */
let catalogData = null;

catalogBtn.addEventListener('click', openCatalog);
modalClose.addEventListener('click', closeCatalog);
catalogModal.addEventListener('click', e => { if (e.target === catalogModal) closeCatalog(); });

catalogSearch.addEventListener('input', () => {
  if (catalogData) renderCatalog(catalogData, catalogSearch.value.toLowerCase());
});

async function openCatalog() {
  catalogModal.style.display = 'flex';
  if (!catalogData) {
    try {
      const resp = await fetch(`${API_BASE}/api/models`);
      catalogData = await resp.json();
      renderCatalog(catalogData, '');
    } catch {
      catalogBody.innerHTML = '<p style="color:var(--tier1);padding:20px">Could not load model catalog.</p>';
    }
  }
}

function closeCatalog() {
  catalogModal.style.display = 'none';
}

function renderCatalog(models, filter) {
  const filtered = filter
    ? models.filter(m => m.name.toLowerCase().includes(filter) || m.id.toLowerCase().includes(filter) || m.provider.toLowerCase().includes(filter))
    : models;

  const tiers = { 1: [], 2: [], 3: [] };
  filtered.forEach(m => {
    if (tiers[m.tier]) tiers[m.tier].push(m);
  });

  const tierTitles = { 1: 'Tier 1 — Frontier / High Complexity', 2: 'Tier 2 — Balanced / Medium', 3: 'Tier 3 — Efficient / Low Cost' };
  const tierClasses = { 1: 't1', 2: 't2', 3: 't3' };

  catalogBody.innerHTML = [1, 2, 3].map(t => {
    const ms = tiers[t];
    if (!ms.length) return '';
    return `
      <div class="catalog-tier-group">
        <div class="catalog-tier-title ${tierClasses[t]}">${tierTitles[t]} (${ms.length} models)</div>
        <div class="catalog-grid">
          ${ms.map(m => `
            <div class="catalog-card">
              <div class="catalog-card-name">${escapeHtml(m.name)}</div>
              <div class="catalog-card-id">${escapeHtml(m.id)}</div>
              <div class="catalog-card-meta">
                <span class="catalog-meta-tag">${(m.context_window/1000).toFixed(0)}K ctx</span>
                ${m.price_per_million_tokens > 0 ? `<span class="catalog-meta-tag">$${m.price_per_million_tokens.toFixed(2)}/M</span>` : ''}
                ${m.supports_vision ? `<span class="catalog-meta-tag highlight">👁 Vision</span>` : ''}
                ${m.supports_thinking ? `<span class="catalog-meta-tag highlight">🧠 Thinking</span>` : ''}
                ${m.supports_coding ? `<span class="catalog-meta-tag highlight">💻 Coding</span>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');

  if (!filtered.length) {
    catalogBody.innerHTML = '<p style="color:var(--text-muted);padding:20px;text-align:center">No models match your search.</p>';
  }
}

/* ── Sidebar toggles ────────────────────────────────────────────────── */
sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
mobileToggle.addEventListener('click', () => sidebar.classList.toggle('open'));

/* ── New session ────────────────────────────────────────────────────── */
newChatBtn.addEventListener('click', () => {
  messages.innerHTML = '';
  emptyState.style.display = 'flex';
  stats = { total: 0, tier1: 0, tier2: 0, tier3: 0, totalMs: 0 };
  updateStats({ tier: 2, total_time_ms: 0 });
  document.getElementById('statTotal').textContent  = '0';
  document.getElementById('statAvgTime').textContent = '—';
  document.getElementById('statTier1').textContent  = '0';
  document.getElementById('statTier3').textContent  = '0';
  sidebar.classList.remove('open');
});

/* ── Health check ───────────────────────────────────────────────────── */
async function checkHealth() {
  try {
    const resp = await fetch(`${API_BASE}/api/health`);
    const data = await resp.json();
    if (data.groq_configured) {
      statusDot.className = 'status-dot online';
      statusText.textContent = 'Groq LLM Active';
    } else {
      statusDot.className = 'status-dot mock';
      statusText.textContent = 'Mock Mode (no key)';
    }
  } catch {
    statusDot.className = 'status-dot offline';
    statusText.textContent = 'Backend offline';
  }
}

checkHealth();

/* ── Helpers ────────────────────────────────────────────────────────── */
function scrollToBottom() {
  setTimeout(() => {
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
  }, 50);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function eyeIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
}
function brainIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>`;
}
function codeIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;
}
function routerIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`;
}
