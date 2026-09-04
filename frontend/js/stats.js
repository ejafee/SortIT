/* ============================================================
   SortIt — Stats & History Dashboard (stats.js)
   ============================================================ */

import { getStats, getScanHistory, clearHistory } from './storage.js';

const TYPE_LABELS = {
  plastic: 'Plastic',
  paper: 'Paper',
  glass: 'Glass',
  organic: 'Organic',
  ewaste: 'E-Waste',
  hazardous: 'Hazardous',
  unknown: 'Unknown',
};

export function renderStats() {
  const stats = getStats();
  const totalEl = document.getElementById('stat-total');
  const avgEl = document.getElementById('stat-avg-conf');
  const corrEl = document.getElementById('stat-corrections');

  if (totalEl) totalEl.textContent = stats.total;
  if (avgEl) avgEl.textContent = stats.total ? stats.avgConfidence + '%' : '—';
  if (corrEl) corrEl.textContent = stats.correctionsCount;

  const chartContainer = document.getElementById('chart-bars');
  if (!chartContainer) return;

  if (stats.total === 0) {
    chartContainer.innerHTML = '<div class="empty-state"><span>📊</span>No scans yet — try scanning something!</div>';
    return;
  }

  const max = Math.max(1, ...Object.values(stats.byType));
  chartContainer.innerHTML = '';
  Object.entries(stats.byType).forEach(([type, count]) => {
    if (count === 0) return;
    const row = document.createElement('div');
    row.className = 'chart-bar-row';
    row.innerHTML = `
      <span class="chart-label">${TYPE_LABELS[type] || type}</span>
      <div class="chart-track"><div class="chart-bar" style="width:${(count/max)*100}%"></div></div>
      <span class="chart-count">${count}</span>
    `;
    chartContainer.appendChild(row);
  });
}

export function renderHistory() {
  const list = document.getElementById('history-list');
  if (!list) return;
  const history = getScanHistory();

  if (history.length === 0) {
    list.innerHTML = '<div class="empty-state"><span>📭</span>No scans yet — try scanning something!</div>';
    return;
  }

  list.innerHTML = '';
  history.forEach(item => {
    const type = item.corrected_type || item.waste_type || 'unknown';
    const el = document.createElement('div');
    el.className = 'history-item';
    el.innerHTML = `
      <div>
        <div><strong>${escapeHtml(item.waste_name || 'Unknown')}</strong>
          ${item.was_corrected ? '<span class="history-tag corrected">Corrected → ' + escapeHtml(item.corrected_type) + '</span>' : ''}
        </div>
        <div class="history-meta">${formatDate(item.timestamp)} · ${item.confidence ?? '—'}%</div>
      </div>
      <span class="history-tag">${TYPE_LABELS[type] || type}</span>
    `;
    list.appendChild(el);
  });
}

export function renderAll() {
  renderStats();
  renderHistory();
}

export function attachClearHistory(handler) {
  const btn = document.getElementById('clear-history-btn');
  if (btn) btn.addEventListener('click', () => {
    if (confirm('Clear all scan history? This cannot be undone.')) {
      clearHistory();
      renderAll();
    }
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[m]));
}

function formatDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch { return iso || '—'; }
}
