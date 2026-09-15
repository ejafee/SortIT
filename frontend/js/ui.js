/* ============================================================
   SortIt — UI Rendering & DOM helpers (ui.js)
   ============================================================ */

const WASTE_STYLES = {
  plastic:   { icon: '🧴', color: '#3498DB', bg: '#EBF5FB' },
  paper:     { icon: '📄', color: '#F39C12', bg: '#FEF9E7' },
  glass:     { icon: '🫙', color: '#1ABC9C', bg: '#E8F8F5' },
  organic:   { icon: '🌿', color: '#2ECC71', bg: '#EAFAF1' },
  ewaste:    { icon: '📱', color: '#9B59B6', bg: '#F5EEF8' },
  hazardous: { icon: '⚠️', color: '#E74C3C', bg: '#FDEDEC' },
  unknown:   { icon: '❓', color: '#95A5A6', bg: '#F2F3F4' },
};

const WASTE_TYPE_OPTIONS = [
  'plastic', 'paper', 'glass', 'organic', 'ewaste', 'hazardous', 'unknown'
];

let currentScanRecord = null;
let currentResultData = null;

export function showPreview(src) {
  document.getElementById('preview-img').src = src;
  document.getElementById('preview-wrap').style.display = 'block';
  document.getElementById('analyze-btn').style.display = 'block';
  document.getElementById('result-card').style.display = 'none';
  hideError();
}

export function showLoading() {
  const btn = document.getElementById('analyze-btn');
  btn.textContent = '⏳ Analyzing…';
  btn.disabled = true;
  hideError();
}

export function resetAnalyzeButton() {
  const btn = document.getElementById('analyze-btn');
  btn.textContent = '🔍 Identify This Waste!';
  btn.disabled = false;
}

export function showError(message, showDetails = false) {
  const banner = document.getElementById('error-banner');
  banner.textContent = '⚠️ ' + message;
  if (showDetails) {
    const link = document.createElement('a');
    link.href = '#tab-history';
    link.textContent = 'See error details';
    link.addEventListener('click', event => {
      event.preventDefault();
      switchTab('history');
      document.getElementById('tab-history')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    banner.append(' ', link);
  }
  banner.style.display = 'block';
}

export function hideError() {
  const banner = document.getElementById('error-banner');
  if (banner) banner.style.display = 'none';
}

/**
 * Render classification result and return the scan record for storage.
 */
export function renderResult(data) {
  currentResultData = data;
  const style = WASTE_STYLES[data.waste_type] || WASTE_STYLES['unknown'];

  const icon = document.getElementById('waste-icon');
  icon.textContent      = style.icon;
  icon.style.background = style.bg;

  document.getElementById('result-name').textContent = data.waste_name || 'Unknown Waste';
  document.getElementById('result-sub').textContent  = data.waste_detail || '';
  document.getElementById('result-header').style.borderBottom = `3px solid ${style.color}`;

  const conf = Number(data.confidence) || 0;
  document.getElementById('conf-fill').style.width = conf + '%';
  document.getElementById('conf-pct').textContent  = conf + '% confidence';

  const warning = document.getElementById('warning-banner');
  if (data.below_threshold) {
    warning.style.display = 'block';
  } else {
    warning.style.display = 'none';
  }

  const ul = document.getElementById('instruction-list');
  ul.innerHTML = '';
  (data.instructions || []).forEach(step => {
    const li = document.createElement('li');
    li.textContent = step;
    ul.appendChild(li);
  });

  document.getElementById('tip-box').textContent = data.tip || '';

  // Populate correction select
  const select = document.getElementById('correct-type');
  select.innerHTML = '';
  WASTE_TYPE_OPTIONS.forEach(opt => {
    const el = document.createElement('option');
    el.value = opt;
    el.textContent = opt;
    if (opt === data.waste_type) el.selected = true;
    select.appendChild(el);
  });
  document.getElementById('correction-form').style.display = 'none';

  document.getElementById('result-card').style.display = 'block';
  document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'start' });

  return {
    waste_type: data.waste_type,
    waste_name: data.waste_name,
    confidence: conf,
    was_corrected: false,
    corrected_type: null,
  };
}

export function getCurrentResultData() {
  return currentResultData;
}

export function getCurrentScanRecord() {
  return currentScanRecord;
}

export function setCurrentScanRecord(record) {
  currentScanRecord = record;
}

export function resetAll() {
  currentScanRecord = null;
  currentResultData = null;
  document.getElementById('preview-wrap').style.display = 'none';
  document.getElementById('analyze-btn').style.display  = 'none';
  document.getElementById('result-card').style.display  = 'none';
  document.getElementById('correction-form').style.display = 'none';
  hideError();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

export function switchTab(tabName) {
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`.nav-tab[data-tab="${tabName}"]`)?.classList.add('active');
  document.getElementById(`tab-${tabName}`)?.classList.add('active');
}

export function toggleCorrectionForm() {
  const form = document.getElementById('correction-form');
  form.style.display = form.style.display === 'none' || form.style.display === '' ? 'block' : 'none';
}
