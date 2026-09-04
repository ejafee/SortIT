/* ============================================================
   SortIt — App Entry Point (app.js)
   ============================================================ */

import { analyzeImage, submitCorrection } from './api.js';
import { saveScan, markScanCorrected } from './storage.js';
import {
  showPreview, showLoading, resetAnalyzeButton, showError, hideError,
  renderResult, resetAll, switchTab, toggleCorrectionForm,
  getCurrentResultData, getCurrentScanRecord, setCurrentScanRecord,
} from './ui.js';
import { renderAll, attachClearHistory } from './stats.js';

let capturedBlob = null;
let mediaStream = null;

/* ── TAB SWITCHING ── */
function initTabs() {
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const name = tab.dataset.tab;
      switchTab(name);
      if (name === 'history' || name === 'stats') renderAll();
    });
  });
}

/* ── CAMERA ── */
async function openCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    document.getElementById('camera-feed').srcObject = mediaStream;
    document.getElementById('camera-wrap').style.display = 'block';
    document.getElementById('analyze-btn').style.display = 'none';
    hideError();
  } catch {
    showError('Camera not accessible. Please allow camera permissions and try again.');
  }
}

function snapPhoto() {
  const video  = document.getElementById('camera-feed');
  const canvas = document.getElementById('snap-canvas');
  if (!video.videoWidth) return;
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    capturedBlob = blob;
    showPreview(canvas.toDataURL('image/jpeg'));
    stopCamera();
  }, 'image/jpeg', 0.9);
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop());
    mediaStream = null;
  }
  document.getElementById('camera-wrap').style.display = 'none';
}

/* ── ANALYZE ── */
async function handleAnalyze() {
  if (!capturedBlob) {
    showError('Please take a photo first.');
    return;
  }
  showLoading();
  try {
    const data = await analyzeImage(capturedBlob);
    const record = renderResult(data);
    const saved = saveScan(record);
    setCurrentScanRecord(saved);
  } catch (err) {
    const message = err.error_type === 'GeminiAPIError'
      ? 'AI service is unavailable right now. Please try again in a moment.'
      : err.error_type === 'InvalidImageError'
      ? 'Image could not be read. Please retake the photo.'
      : err.error_type === 'ClassificationParseError'
      ? 'AI response was unclear. Please retake the photo with a clearer angle.'
      : (err.message || 'Could not reach the server. Is the backend running?');
    showError(message);
  } finally {
    resetAnalyzeButton();
  }
}

/* ── CORRECTION ── */
async function handleSubmitCorrection() {
  const result = getCurrentResultData();
  const record = getCurrentScanRecord();
  if (!result) return;

  const select = document.getElementById('correct-type');
  const note   = document.getElementById('correct-note');
  const correctedType = select.value;
  const noteText = note.value || '';

  try {
    await submitCorrection(result, correctedType, noteText);
    if (record) markScanCorrected(record.id, correctedType);
    document.getElementById('correction-form').style.display = 'none';
    showError('Thanks — we have logged your correction to help us improve.');
    document.getElementById('error-banner').style.background = '#E8F5E9';
    document.getElementById('error-banner').style.borderLeftColor = 'var(--green)';
    document.getElementById('error-banner').style.color = 'var(--green)';
  } catch (err) {
    showError('Could not submit correction: ' + (err.message || 'server error'));
  }
}

/* ── INIT ── */
function init() {
  initTabs();

  document.getElementById('camera-btn').addEventListener('click', openCamera);
  document.getElementById('snap-btn').addEventListener('click', snapPhoto);
  document.getElementById('close-cam-btn').addEventListener('click', stopCamera);
  document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);

  document.getElementById('reset-btn').addEventListener('click', resetAll);
  document.getElementById('correct-toggle-btn').addEventListener('click', toggleCorrectionForm);
  document.getElementById('submit-correction-btn').addEventListener('click', handleSubmitCorrection);

  attachClearHistory();
  renderAll();
}

document.addEventListener('DOMContentLoaded', init);
