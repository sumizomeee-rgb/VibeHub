"""
VibeHub Design System
Shared styles, colors, and components for a cohesive modern SaaS look.
"""

from nicegui import ui

# ---- Design Tokens ----
BRAND = {
    "primary": "#6366f1",
    "primary_light": "#818cf8",
    "primary_dark": "#4f46e5",
    "accent": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "surface": "#ffffff",
    "surface_dim": "#f8fafc",
    "surface_dark": "#0f172a",
    "text": "#0f172a",
    "text_secondary": "#64748b",
    "text_muted": "#94a3b8",
    "border": "#e2e8f0",
}

# ---- Google Fonts ----
_FONTS_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
"""

# ---- Global CSS ----
_GLOBAL_CSS = """
<style>
:root {
    --vh-primary: #6366f1;
    --vh-primary-light: #818cf8;
    --vh-accent: #06b6d4;
    --vh-success: #10b981;
    --vh-error: #ef4444;
    --vh-surface: #ffffff;
    --vh-bg: #f1f5f9;
    --vh-text: #0f172a;
    --vh-text-secondary: #64748b;
    --vh-border: #e2e8f0;
    --vh-radius: 16px;
    --vh-radius-sm: 10px;
    --vh-shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    --vh-shadow-md: 0 4px 16px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
    --vh-shadow-lg: 0 12px 40px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);
    --vh-shadow-glow: 0 0 24px rgba(99, 102, 241, 0.15);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--vh-bg) !important;
    color: var(--vh-text);
    -webkit-font-smoothing: antialiased;
}

/* ---- Header ---- */
.vh-header {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #818cf8 100%) !important;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.25) !important;
    backdrop-filter: blur(12px);
    border-bottom: none !important;
}

/* ---- Cards ---- */
.vh-card {
    background: var(--vh-surface);
    border: 1px solid var(--vh-border);
    border-radius: var(--vh-radius) !important;
    box-shadow: var(--vh-shadow-sm);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}
.vh-card:hover {
    box-shadow: var(--vh-shadow-lg);
    transform: translateY(-3px);
    border-color: var(--vh-primary-light);
}

/* ---- Buttons ---- */
.vh-btn-primary {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    transition: all 0.2s ease !important;
    text-transform: none !important;
}
.vh-btn-primary:hover {
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-1px);
}

.vh-btn-ghost {
    border-radius: 10px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s ease !important;
}
.vh-btn-ghost:hover {
    background: rgba(99, 102, 241, 0.08) !important;
}

.vh-btn-outline {
    border: 1.5px solid var(--vh-border) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s ease !important;
}
.vh-btn-outline:hover {
    border-color: var(--vh-primary) !important;
    color: var(--vh-primary) !important;
    background: rgba(99, 102, 241, 0.04) !important;
}

/* ---- Status Indicators ---- */
.vh-status-dot {
    width: 10px; height: 10px; border-radius: 50%; display: inline-block;
    position: relative;
}
.vh-status-dot::after {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    opacity: 0.3;
}
.vh-status-running {
    background: var(--vh-success);
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}
.vh-status-running::after {
    background: var(--vh-success);
    animation: statusPulse 2s ease-in-out infinite;
}
.vh-status-error {
    background: var(--vh-error);
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}
.vh-status-stopped {
    background: #cbd5e1;
}

/* ---- Terminal Log ---- */
.vh-terminal {
    background: #0f172a !important;
    color: #e2e8f0;
    border-radius: var(--vh-radius) !important;
    font-family: 'JetBrains Mono', 'Cascadia Code', monospace !important;
    font-size: 12.5px;
    border: 1px solid #1e293b;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
}
.vh-terminal .q-virtual-scroll__content {
    padding: 16px 20px;
    line-height: 1.7;
}

/* ---- Progress Stepper ---- */
.vh-stepper {
    background: var(--vh-surface);
    border: 1px solid var(--vh-border);
    border-radius: var(--vh-radius) !important;
    padding: 20px 28px;
    box-shadow: var(--vh-shadow-sm);
}
.vh-step-icon {
    width: 40px; height: 40px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.vh-step-pending .vh-step-icon {
    background: #f1f5f9;
    color: #94a3b8;
}
.vh-step-active .vh-step-icon {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    color: white;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    animation: stepPulse 2s ease-in-out infinite;
}
.vh-step-done .vh-step-icon {
    background: linear-gradient(135deg, #10b981, #34d399);
    color: white;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}
.vh-step-connector {
    height: 2px;
    flex: 1;
    background: #e2e8f0;
    margin: 0 4px;
    border-radius: 1px;
    transition: background 0.4s ease;
}
.vh-step-connector-done {
    background: linear-gradient(90deg, #10b981, #34d399);
}
.vh-step-connector-active {
    background: linear-gradient(90deg, #10b981, #6366f1);
}

/* ---- Toast Notification ---- */
.vh-toast-container {
    position: fixed;
    top: 80px;
    right: 24px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
}
.vh-toast {
    pointer-events: auto;
    min-width: 360px;
    max-width: 440px;
    padding: 16px 20px;
    border-radius: 14px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    animation: toastIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    backdrop-filter: blur(16px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.06);
}
.vh-toast-success {
    background: linear-gradient(135deg, rgba(16,185,129,0.95), rgba(5,150,105,0.95));
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
}
.vh-toast-error {
    background: linear-gradient(135deg, rgba(239,68,68,0.95), rgba(220,38,38,0.95));
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
}
.vh-toast-info {
    background: linear-gradient(135deg, rgba(99,102,241,0.95), rgba(79,70,229,0.95));
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
}
.vh-toast-icon {
    font-size: 24px;
    flex-shrink: 0;
    margin-top: 1px;
}
.vh-toast-body { flex: 1; }
.vh-toast-title {
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 2px;
}
.vh-toast-msg {
    font-size: 13px;
    opacity: 0.9;
}
.vh-toast-close {
    cursor: pointer;
    opacity: 0.6;
    transition: opacity 0.2s;
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 1px;
}
.vh-toast-close:hover { opacity: 1; }
.vh-toast-exit {
    animation: toastOut 0.35s cubic-bezier(0.4, 0, 1, 1) forwards;
}

/* ---- Success Celebration ---- */
.vh-celebrate {
    animation: celebrateIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.vh-celebrate-icon {
    animation: celebrateBounce 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s both;
}
.vh-confetti-particle {
    position: absolute;
    width: 8px; height: 8px;
    border-radius: 2px;
    animation: confettiFall 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    pointer-events: none;
}

/* ---- Input ---- */
.vh-input .q-field__control {
    border-radius: 12px !important;
}
.vh-input .q-field--outlined .q-field__control:before {
    border-color: var(--vh-border) !important;
}
.vh-input .q-field--outlined .q-field__control:hover:before {
    border-color: var(--vh-primary-light) !important;
}
.vh-input .q-field--focused .q-field__control:after {
    border-color: var(--vh-primary) !important;
    border-width: 2px !important;
}

/* ---- Empty State ---- */
.vh-empty-icon {
    width: 120px; height: 120px;
    border-radius: 32px;
    background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto;
}

/* ---- Animations ---- */
@keyframes statusPulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0; transform: scale(1.8); }
}
@keyframes stepPulse {
    0%, 100% { box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35); }
    50% { box-shadow: 0 4px 24px rgba(99, 102, 241, 0.55); }
}
@keyframes toastIn {
    from { opacity: 0; transform: translateX(80px) scale(0.95); }
    to { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes toastOut {
    from { opacity: 1; transform: translateX(0) scale(1); }
    to { opacity: 0; transform: translateX(80px) scale(0.9); }
}
@keyframes celebrateIn {
    from { opacity: 0; transform: scale(0.9) translateY(30px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes celebrateBounce {
    from { opacity: 0; transform: scale(0) rotate(-15deg); }
    to { opacity: 1; transform: scale(1) rotate(0deg); }
}
@keyframes confettiFall {
    0% { opacity: 1; transform: translateY(0) rotate(0deg); }
    100% { opacity: 0; transform: translateY(120px) rotate(720deg); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
.vh-fade-in {
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ---- Badge ---- */
.vh-badge {
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.vh-badge-green {
    background: rgba(16, 185, 129, 0.1);
    color: #059669;
}
.vh-badge-red {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
}
.vh-badge-grey {
    background: rgba(148, 163, 184, 0.15);
    color: #64748b;
}
</style>
"""

# ---- Toast JS (replaces native Notification + ui.notify) ----
_TOAST_JS = """
<script>
window.__vhToasts = [];
window.__vhToastContainer = null;

function vhEnsureContainer() {
    if (!window.__vhToastContainer) {
        var c = document.createElement('div');
        c.className = 'vh-toast-container';
        document.body.appendChild(c);
        window.__vhToastContainer = c;
    }
    return window.__vhToastContainer;
}

function vhToast(type, title, msg, duration) {
    duration = duration || 6000;
    var container = vhEnsureContainer();
    var icons = { success: 'check_circle', error: 'error', info: 'info' };

    var el = document.createElement('div');
    el.className = 'vh-toast vh-toast-' + type;
    el.innerHTML = '<span class="material-icons vh-toast-icon">' + (icons[type] || 'info') + '</span>'
        + '<div class="vh-toast-body">'
        + '<div class="vh-toast-title">' + title + '</div>'
        + (msg ? '<div class="vh-toast-msg">' + msg + '</div>' : '')
        + '</div>'
        + '<span class="material-icons vh-toast-close" onclick="vhDismissToast(this.parentElement)">close</span>';

    container.appendChild(el);

    // Auto dismiss
    var timer = setTimeout(function() { vhDismissToast(el); }, duration);
    el.__timer = timer;
}

function vhDismissToast(el) {
    if (!el || el.__dismissed) return;
    el.__dismissed = true;
    clearTimeout(el.__timer);
    el.classList.add('vh-toast-exit');
    setTimeout(function() { el.remove(); }, 350);
}

// Confetti burst for celebrations
function vhConfetti(targetEl) {
    var colors = ['#6366f1','#818cf8','#06b6d4','#10b981','#f59e0b','#ec4899'];
    var rect = targetEl.getBoundingClientRect();
    var cx = rect.left + rect.width / 2;
    var cy = rect.top + rect.height / 2;

    for (var i = 0; i < 24; i++) {
        var p = document.createElement('div');
        p.className = 'vh-confetti-particle';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.left = cx + 'px';
        p.style.top = cy + 'px';
        var angle = (Math.PI * 2 * i) / 24 + (Math.random() - 0.5) * 0.5;
        var dist = 60 + Math.random() * 80;
        p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
        p.style.setProperty('--ty', Math.sin(angle) * dist - 40 + 'px');
        p.style.animation = 'confettiFall ' + (0.8 + Math.random() * 0.7) + 's cubic-bezier(0.4,0,0.2,1) forwards';
        p.style.transform = 'translate(var(--tx), var(--ty))';
        document.body.appendChild(p);
        setTimeout(function(el) { el.remove(); }.bind(null, p), 2000);
    }
}
</script>
"""


def apply_theme():
    """Call once per page to inject the VibeHub design system."""
    ui.colors(primary=BRAND["primary"])
    ui.add_head_html(_FONTS_HTML)
    ui.add_head_html(_GLOBAL_CSS)
    ui.add_head_html(_TOAST_JS)
