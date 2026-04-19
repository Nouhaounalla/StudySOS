/* =============================================
   StudySOS – Shared JS Utilities
   ============================================= */

// ---- Toast notifications ----
function showToast(message, type = 'default') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ---- CSRF token ----
function getCsrfToken() {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

// ---- API helper ----
async function api(method, url, data = null, isFormData = false) {
  const options = {
    method,
    credentials: 'include',
    headers: { 'X-CSRFToken': getCsrfToken() },
  };
  if (data && !isFormData) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(data);
  } else if (data && isFormData) {
    options.body = data; // FormData
  }
  const res = await fetch(url, options);
  const json = res.ok ? await res.json().catch(() => ({})) : await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data: json };
}

const API = {
  get:    (url)        => api('GET', url),
  post:   (url, data)  => api('POST', url, data),
  patch:  (url, data)  => api('PATCH', url, data),
  delete: (url)        => api('DELETE', url),
  upload: (url, form)  => api('POST', url, form, true),
};

// ---- Modal helpers ----
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.style.display = 'flex'; requestAnimationFrame(() => el.classList.add('open')); }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); setTimeout(() => el.style.display = 'none', 200); }
}
// Close on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    setTimeout(() => e.target.style.display = 'none', 200);
  }
});

// ---- Dropdown toggle ----
document.addEventListener('click', e => {
  const trigger = e.target.closest('[data-dropdown]');
  if (trigger) {
    e.stopPropagation();
    const target = document.getElementById(trigger.dataset.dropdown);
    if (target) target.classList.toggle('open');
    return;
  }
  document.querySelectorAll('.dropdown-menu.open, .notif-dropdown.open')
    .forEach(el => el.classList.remove('open'));
});

// ---- Tabs ----
function initTabs(containerSelector) {
  document.querySelectorAll(`${containerSelector} .tab-btn`).forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = btn.dataset.tab;
      document.querySelectorAll(`${containerSelector} .tab-btn`).forEach(b => b.classList.remove('active'));
      document.querySelectorAll(`${containerSelector} .tab-panel`).forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const el = document.getElementById(panel);
      if (el) el.classList.add('active');
    });
  });
}

// ---- Relative time ----
function relativeTime(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'à l\'instant';
  if (mins < 60) return `il y a ${mins} min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `il y a ${hours}h`;
  const days = Math.floor(hours / 24);
  return `il y a ${days}j`;
}

// ---- Avatar HTML ----
function avatarHtml(user, size = '') {
  const cls = `avatar ${size}`;
  if (user.profile_photo) {
    return `<div class="${cls}"><img src="${user.profile_photo}" alt="${user.username}"></div>`;
  }
  return `<div class="${cls}">${user.initials || '?'}</div>`;
}

// ---- Stars HTML ----
function starsHtml(score, max = 5) {
  return Array.from({ length: max }, (_, i) =>
    `<span class="star ${i < Math.round(score) ? 'filled' : ''}">★</span>`
  ).join('');
}

// ---- Notification WebSocket ----
function connectNotifications() {
  const ws = new WebSocket(`ws://${location.host}/ws/notifications/`);
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.message) {
      showToast(data.message, 'info');
      // Update badge
      const badge = document.getElementById('notif-badge');
      if (badge) {
        const count = parseInt(badge.textContent || '0') + 1;
        badge.textContent = count;
        badge.style.display = 'flex';
      }
    }
  };
  ws.onerror = () => {}; // silent
}

// ---- On DOM ready ----
document.addEventListener('DOMContentLoaded', () => {
  initTabs('body');
  connectNotifications();
  // Load unread count
  API.get('/api/notifications/unread-count/').then(r => {
    if (r.ok && r.data.count > 0) {
      const badge = document.getElementById('notif-badge');
      if (badge) { badge.textContent = r.data.count; badge.style.display = 'flex'; }
    }
  });
});
