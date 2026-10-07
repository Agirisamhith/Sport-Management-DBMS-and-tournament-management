// =============================================================================
// main.js — Shared utilities for the WoxuDB frontend
// =============================================================================

const API = '/api';

// --- Toast notifications ---
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// --- Modal helpers ---
function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

// Close modal on backdrop click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// --- API helpers ---
async function apiFetch(url, options = {}) {
  const res = await fetch(API + url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  if (res.status === 204) return null;
  return res.json();
}

async function apiGet(url)           { return apiFetch(url); }
async function apiPost(url, body)    { return apiFetch(url, { method: 'POST',   body: JSON.stringify(body) }); }
async function apiPut(url, body)     { return apiFetch(url, { method: 'PUT',    body: JSON.stringify(body) }); }
async function apiPatch(url, body)   { return apiFetch(url, { method: 'PATCH',  body: JSON.stringify(body) }); }
async function apiDelete(url)        { return apiFetch(url, { method: 'DELETE' }); }

// --- Formatting helpers ---
function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(d) {
  if (!d) return '—';
  const dt = new Date(d);
  return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) + ' ' +
         dt.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
}

function formatCurrency(n) {
  return '₹' + parseFloat(n || 0).toFixed(2);
}

function statusBadge(status) {
  const map = {
    'Active':    'badge-success',
    'Expired':   'badge-danger',
    'Cancelled': 'badge-muted',
    'On Loan':   'badge-warning',
    'Returned':  'badge-success',
    'Available': 'badge-success',
    'Low Stock': 'badge-warning',
    'Out of Stock': 'badge-danger',
  };
  return `<span class="badge ${map[status] || 'badge-info'}">${status}</span>`;
}

// --- Active nav highlighting ---
(function () {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href && (path === href || (href !== '/' && path.startsWith(href)))) {
      item.classList.add('active');
    }
  });
})();
