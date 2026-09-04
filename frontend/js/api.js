/* ============================================================
   SortIt — API Client (api.js)
   ============================================================ */

const API_BASE_URL = 'http://localhost:5000';

/**
 * Send image blob to POST /analyze
 */
export async function analyzeImage(imageBlob) {
  const formData = new FormData();
  formData.append('image', imageBlob, 'waste.jpg');

  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.message || 'Server error occurred');
    err.error_type = data.error_type || 'UnknownError';
    err.status = res.status;
    throw err;
  }

  return data;
}

/**
 * Send user correction to POST /correct
 */
export async function submitCorrection(originalResult, correctedType, note = '') {
  const payload = {
    original_result: originalResult,
    corrected_waste_type: correctedType,
    note: note.trim(),
    timestamp: new Date().toISOString(),
  };

  const res = await fetch(`${API_BASE_URL}/correct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.message || 'Failed to submit correction');
    err.status = res.status;
    throw err;
  }

  return data;
}
