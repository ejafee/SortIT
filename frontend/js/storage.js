/* ============================================================
   SortIt — Storage Layer (storage.js)
   Interface backed by browser localStorage
   ============================================================ */

const STORAGE_KEY = 'sortit_scan_history_v1';

export function saveScan(scanRecord) {
  const history = getScanHistory();
  const record = {
    id: scanRecord.id || 'scan_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
    timestamp: scanRecord.timestamp || new Date().toISOString(),
    waste_type: scanRecord.waste_type,
    waste_name: scanRecord.waste_name,
    confidence: scanRecord.confidence,
    is_error: !!scanRecord.is_error,
    error_message: scanRecord.error_message || null,
    was_corrected: !!scanRecord.was_corrected,
    corrected_type: scanRecord.corrected_type || null,
  };
  history.unshift(record);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.warn('LocalStorage save failed:', e);
  }
  return record;
}

export function markScanCorrected(scanId, correctedType) {
  const history = getScanHistory();
  const item = history.find(s => s.id === scanId || (s.waste_name && s.waste_type));
  if (item) {
    item.was_corrected = true;
    item.corrected_type = correctedType;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
      console.warn('LocalStorage update failed:', e);
    }
  }
}

export function getScanHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Failed to read scan history:', e);
    return [];
  }
}

export function getStats() {
  const history = getScanHistory();
  const total = history.length;
  if (total === 0) {
    return {
      total: 0,
      avgConfidence: 0,
      correctionsCount: 0,
      byType: {},
    };
  }

  const successfulScans = history.filter(s => !s.is_error);
  let totalConf = 0;
  let corrections = 0;
  const byType = {
    plastic: 0,
    paper: 0,
    glass: 0,
    organic: 0,
    ewaste: 0,
    hazardous: 0,
    unknown: 0,
  };

  successfulScans.forEach(s => {
    totalConf += Number(s.confidence) || 0;
    if (s.was_corrected) corrections++;
    const type = s.corrected_type || s.waste_type || 'unknown';
    byType[type] = (byType[type] || 0) + 1;
  });

  return {
    total,
    avgConfidence: successfulScans.length ? Math.round(totalConf / successfulScans.length) : 0,
    correctionsCount: corrections,
    byType,
  };
}

export function clearHistory() {
  localStorage.removeItem(STORAGE_KEY);
}
