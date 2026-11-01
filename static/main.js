/* ════════════════════════════════════════════════════════
   CD 2.0 – main.js  (multi-error rendering + CodeMirror)
   ════════════════════════════════════════════════════════ */

"use strict";

// ──────────────────────────────────────────────────────────
//  State
// ──────────────────────────────────────────────────────────
let selectedFile = null;
let cmEditor     = null;   // CodeMirror instance

// ──────────────────────────────────────────────────────────
//  Example snippets
// ──────────────────────────────────────────────────────────
const EXAMPLES = {
  infinite_loop: `#include <iostream>
int main() {
    int x = 0;
    while (true) {
        x++;
        // No break — infinite loop!
    }
    return 0;
}`,
  multi_error: `#include <stdio.h>
#include <cstring>
int main() {
    char buf[8];
    char inp[64] = "%x %x %x";
    // Error 1: buffer overflow via strcpy
    strcpy(buf, "This string is way too long for buf!");
    // Error 2: format-string vulnerability
    printf(inp);
    return 0;
}`,
  type_mismatch: `#include <iostream>
int main() {
    // Error: assigning string literal to int
    int x = "hello";
    std::cout << x << std::endl;
    return 0;
}`,
  buffer_overflow: `#include <cstring>
#include <iostream>
int main() {
    char buf[8];
    // Error: strcpy to buffer too small
    strcpy(buf, "This is definitely too long!");
    std::cout << buf << std::endl;
    return 0;
}`,
  null_ptr: `#include <iostream>
int main() {
    int* p = nullptr;
    // Error: dereferencing nullptr
    *p = 42;
    std::cout << *p << std::endl;
    return 0;
}`,
  clean: `#include <iostream>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int val = 5;
    std::cout << "5! = " << factorial(val) << std::endl;
    return 0;
}`,
};

// ──────────────────────────────────────────────────────────
//  Initialise CodeMirror editor
// ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initCodeMirror();
  spawnParticles();
});

function initCodeMirror() {
  const textarea = document.getElementById('code-input');
  if (typeof CodeMirror === 'undefined') {
    // CodeMirror failed to load — fall back to plain textarea
    textarea.style.display = 'block';
    textarea.style.width   = '100%';
    textarea.style.height  = '260px';
    return;
  }
  cmEditor = CodeMirror(document.getElementById('cm-editor'), {
    // Start empty so reported line numbers match user input exactly.
    value:        '',
    mode:         'text/x-c++src',
    theme:        'eclipse',
    lineNumbers:  true,
    indentUnit:   4,
    tabSize:      4,
    indentWithTabs: false,
    styleActiveLine: true,
    autoRefresh:  true,
    extraKeys: {
      Tab: cm => cm.execCommand('indentMore'),
      'Shift-Tab': cm => cm.execCommand('indentLess'),
    },
  });
}

// ──────────────────────────────────────────────────────────
//  Floating particles
// ──────────────────────────────────────────────────────────
function spawnParticles() {
  const container = document.getElementById('particles');
  if (!container) return;
  for (let i = 0; i < 14; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size  = Math.random() * 180 + 60;
    p.style.cssText = [
      `width:${size}px`, `height:${size}px`,
      `left:${Math.random() * 100}%`,
      `animation-duration:${Math.random() * 18 + 12}s`,
      `animation-delay:${Math.random() * 10}s`,
      `opacity:${Math.random() * .18 + .04}`,
    ].join(';');
    container.appendChild(p);
  }
}

// ──────────────────────────────────────────────────────────
//  Tab switching
// ──────────────────────────────────────────────────────────
function switchTab(tab) {
  ['upload', 'paste', 'examples'].forEach(t => {
    document.getElementById(`panel-${t}`).classList.toggle('hidden', t !== tab);
    const btn = document.getElementById(`tab-${t}`);
    btn.classList.toggle('active', t === tab);
    btn.setAttribute('aria-selected', t === tab);
  });
  if (tab !== 'upload') {
    selectedFile = null;
    document.getElementById('file-label').textContent = 'No file selected';
  }
  if (tab === 'paste' && cmEditor) cmEditor.refresh();
}

// ──────────────────────────────────────────────────────────
//  File handling
// ──────────────────────────────────────────────────────────
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropzone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) applyFile(file);
}
function handleFileSelect(input) {
  if (input.files[0]) applyFile(input.files[0]);
}
function applyFile(file) {
  selectedFile = file;
  document.getElementById('file-label').textContent = `✅ ${file.name}`;
}

// ──────────────────────────────────────────────────────────
//  Example loading
// ──────────────────────────────────────────────────────────
function loadExample(key) {
  const code = EXAMPLES[key];
  if (!code) return;
  // Switch to paste tab and populate editor
  switchTab('paste');
  if (cmEditor) {
    cmEditor.setValue(code);
    cmEditor.refresh();
  } else {
    document.getElementById('code-input').value = code;
  }
}

// ──────────────────────────────────────────────────────────
//  Editor helpers
// ──────────────────────────────────────────────────────────
function clearEditor() {
  if (cmEditor) cmEditor.setValue('');
  else document.getElementById('code-input').value = '';
}
function copyCode() {
  const code = cmEditor ? cmEditor.getValue() : document.getElementById('code-input').value;
  if (!code.trim()) return;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById('copy-btn');
    const orig = btn.textContent;
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = orig, 1500);
  });
}

// ──────────────────────────────────────────────────────────
//  Diagnosis
// ──────────────────────────────────────────────────────────
async function runDiagnosis() {
  const activeTab = document.querySelector('.tab.active')?.id?.replace('tab-', '') || 'upload';
  const isUpload  = activeTab === 'upload';
  const isPaste   = activeTab === 'paste' || activeTab === 'examples';
  const code      = cmEditor ? cmEditor.getValue().trim()
                             : document.getElementById('code-input').value.trim();

  if (isUpload && !selectedFile) { showError('Please select a .cpp file first.'); return; }
  if (isPaste  && !code)         { showError('Please enter or select some C++ code.'); return; }

  setBusy(true);
  hideCards();

  const form = new FormData();
  if (isUpload) {
    form.append('file', selectedFile);
  } else {
    form.append('code', code);
  }

  try {
    const res  = await fetch('/diagnose', { method: 'POST', body: form });
    const data = await res.json();
    if (data.security && data.security.detected) {
  showSecurityThreat(data);
} else if (!res.ok || data.error) {
  showError(data.error || `Server error ${res.status}`);
} else {
  showResult(data);
}
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    setBusy(false);
  }
}

// ──────────────────────────────────────────────────────────
//  Render multi-error result
// ──────────────────────────────────────────────────────────
function showResult(d) {
  const errors   = d.errors || [];
  const summary  = d.summary || {};
  const filename = d.filename || d.file || 'unknown';

  // ── Header ──────────────────────────────────────────────
  document.getElementById('r-filename').textContent = filename;

  const sevBadge = document.getElementById('r-severity-badge');
  const highest  = summary.highest_severity || (errors.length ? errors[0].severity : 'N/A');
  sevBadge.textContent = highest;
  sevBadge.className   = `badge ${severityClass(highest)}`;

  const countBadge = document.getElementById('r-error-count');
  if (errors.length > 0) {
    countBadge.textContent = `${errors.length} Error${errors.length !== 1 ? 's' : ''}`;
    countBadge.classList.add('visible');
  } else {
    countBadge.classList.remove('visible');
  }

  // ── Summary strip ────────────────────────────────────────
  document.getElementById('s-total').textContent = summary.total_errors ?? errors.length;
  document.getElementById('s-inf').textContent   = summary.has_infinite_loop ? '⚠ Yes' : '✅ No';
  document.getElementById('s-sev').textContent   = highest;

  // ── Error list ────────────────────────────────────────────
  const panel  = document.getElementById('errors-panel');
  const noErr  = document.getElementById('no-error-state');
  panel.innerHTML = '';

  if (errors.length === 0) {
    noErr.classList.remove('hidden');
  } else {
    noErr.classList.add('hidden');
    errors.forEach((err, idx) => {
      panel.appendChild(buildErrorEntry(err, idx + 1));
    });
    // Auto-expand first error
    const firstBody = panel.querySelector('.ee-body');
    if (firstBody) {
      firstBody.classList.add('expanded');
      const toggle = panel.querySelector('.ee-toggle');
      if (toggle) toggle.classList.add('open');
    }
  }

  // ── Energy & Analytics ────────────────────────────────────
  const edash = document.getElementById('energy-dashboard');
  if (d.energy || d.carbon) {
    edash.classList.remove('hidden');
    const ej = d.energy ? d.energy.joules : 0;
    const cw = d.energy ? d.energy.watts : 0;
    const cc = d.carbon ? d.carbon.grams_co2 : 0;
    const cNote = d.carbon ? d.carbon.note : '';
    const eNote = d.energy ? d.energy.note : '';
    const dur = d.energy ? d.energy.duration_s : 0;

    document.getElementById('e-joules').textContent = ej < 0.001 ? (ej*1000000).toFixed(0) + ' µJ' : (ej < 1 ? (ej*1000).toFixed(2) + ' mJ' : ej.toFixed(4) + ' J');
    document.getElementById('e-watts').textContent = cw.toFixed(3) + ' W';
    document.getElementById('e-carbon').textContent = cc < 1 ? (cc*1000).toFixed(2) + ' mg CO₂' : cc.toFixed(3) + ' g CO₂';
    document.getElementById('e-source').textContent = eNote;
    document.getElementById('e-c-source').textContent = cNote;
    document.getElementById('e-time').textContent = dur.toFixed(3) + 's duration';
    
    window._lastDiagnosisResult = d;
    renderChart(d);
  } else {
    edash.classList.add('hidden');
  }

  document.getElementById('result-card').classList.remove('hidden');
  document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buildErrorEntry(err, num) {
  const sev     = (err.severity || 'low').toLowerCase();
  const sevKey  = sev === 'critical' ? 'crit' : sev.substring(0, 3);
  const lineStr = err.line && err.line > 0 ? `Line ${err.line}` : 'Global';
  const typeStr = (err.error_type || 'unknown').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  const entry = document.createElement('div');
  entry.className = `error-entry sev-${sev}`;

  entry.innerHTML = `
    <div class="ee-header" onclick="toggleEntry(this)" aria-expanded="false" role="button" tabindex="0">
      <span class="ee-num">${num}</span>
      <span class="ee-line-chip">${lineStr}</span>
      <span class="ee-type">${typeStr}</span>
      <span class="ee-sev-badge ${sevKey}">${err.severity || '—'}</span>
      <span class="ee-toggle" aria-hidden="true">▼</span>
    </div>
    <div class="ee-body">
      <p class="ee-message">${escapeHtml(err.message || '—')}</p>
      <div class="ee-meta">
        <span class="ee-meta-chip"><strong>Category:</strong>&nbsp;${err.category || '—'}</span>
        <span class="ee-meta-chip"><strong>Nature:</strong>&nbsp;${err.nature || '—'}</span>
        <span class="ee-meta-chip"><strong>Error:</strong>&nbsp;${err.error_type || '—'}</span>
      </div>
      <div class="ee-sections">
        <div class="ee-section section-fix">
          <div class="ee-section-head">💡 Fix Suggestion</div>
          <div class="ee-section-body">${escapeHtml(err.suggestion || '—')}</div>
        </div>
        <div class="ee-section section-security">
          <div class="ee-section-head">🔐 Security Impact</div>
          <div class="ee-section-body">${escapeHtml(err.security || '—')}</div>
        </div>
      </div>
    </div>`;

  // Keyboard support
  const header = entry.querySelector('.ee-header');
  header.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleEntry(header); } });

  return entry;
}

function toggleEntry(header) {
  const body   = header.nextElementSibling;
  const toggle = header.querySelector('.ee-toggle');
  const open   = body.classList.toggle('expanded');
  toggle.classList.toggle('open', open);
  header.setAttribute('aria-expanded', open);
}

// ──────────────────────────────────────────────────────────
//  Helpers
// ──────────────────────────────────────────────────────────
function severityClass(sev) {
  const map = { Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low' };
  return map[sev] || 'badge-na';
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showError(msg) {
  document.getElementById('error-msg').textContent = msg;
  document.getElementById('error-card').classList.remove('hidden');
}
function showSecurityThreat(data) {
  const security = data.security;

  const errorCard = document.getElementById('error-card');
  const errorMsg = document.getElementById('error-msg');

  errorMsg.innerHTML = `
    <strong>🚨 Security Threat Detected</strong><br><br>
    <strong>Attack Type:</strong> ${security.attack_type}<br>
    <strong>Risk:</strong> ${security.risk}<br>
    <strong>Action:</strong> ${security.action}<br>
    <strong>Matched Pattern:</strong> ${security.matched_pattern}
  `;

  errorCard.classList.remove('hidden');
}
function hideCards() {
  document.getElementById('result-card').classList.add('hidden');
  document.getElementById('error-card').classList.add('hidden');
}

function setBusy(on) {
  document.getElementById('btn-text').classList.toggle('hidden', on);
  document.getElementById('btn-spinner').classList.toggle('hidden', !on);
  document.getElementById('analyze-btn').disabled = on;
}

function resetForm() {
  hideCards();
  selectedFile = null;
  document.getElementById('file-label').textContent = 'No file selected';
  document.getElementById('file-input').value       = '';
  if (cmEditor) cmEditor.setValue('');
  else document.getElementById('code-input').value = '';
  document.getElementById('errors-panel').innerHTML = '';
  document.getElementById('r-error-count').classList.remove('visible');
  document.getElementById('no-error-state').classList.add('hidden');
  document.getElementById('energy-dashboard').classList.add('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ──────────────────────────────────────────────────────────
//  Charts & Export
// ──────────────────────────────────────────────────────────
let currentChart = null;

function renderChart(d) {
  if (!d.energy_virtual || !d.energy_virtual.stages) return;
  const stages = d.energy_virtual.stages;
  
  const ctx = document.getElementById('energyChart').getContext('2d');
  if (currentChart) currentChart.destroy();
  
  const labels = ['Compile', 'Static Analysis', 'ML Inference', 'Report Gen'];
  const values = [
    stages.compile ? stages.compile.joules : 0,
    stages.static_analysis ? stages.static_analysis.joules : 0,
    stages.ml_inference ? stages.ml_inference.joules : 0,
    stages.report_gen ? stages.report_gen.joules : 0
  ];
  
  // Convert J to mJ for better scale if all are small
  const use_mj = Math.max(...values) < 1;
  const displayValues = use_mj ? values.map(v => v * 1000) : values;
  
  currentChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: use_mj ? 'Energy (mJ)' : 'Energy (Joules)',
        data: displayValues,
        backgroundColor: [
          'rgba(99, 102, 241, 0.7)',
          'rgba(168, 85, 247, 0.7)',
          'rgba(34, 197, 94, 0.7)',
          'rgba(6, 182, 212, 0.7)'
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(168, 85, 247, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(6, 182, 212, 1)'
        ],
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Energy per Stage [VIRTUAL]', color: '#475569' }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(15,23,42,0.08)' }, ticks: { color: '#475569' } },
        x: { grid: { display: false }, ticks: { color: '#475569' } }
      }
    }
  });
}

async function exportReport(fmt) {
  if (!window._lastDiagnosisResult) return;
  
  try {
    const res = await fetch('/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ format: fmt, result: window._lastDiagnosisResult })
    });
    
    if (!res.ok) throw new Error('Export failed');
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cd2_report_${window._lastDiagnosisResult.file || 'code'}.${fmt === 'text' ? 'txt' : fmt}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert("Export failed: " + err.message);
  }
}
