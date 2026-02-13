"""
VibeHub Design System — Warm Bright Premium Theme
Shared styles, colors, and components for a cohesive modern light SaaS look.
"""

from nicegui import ui

# ---- Design Tokens ----
BRAND = {
    "primary": "#6C5CE7",
    "primary_light": "#A29BFE",
    "primary_dark": "#5A4BD1",
    "accent": "#00B894",
    "success": "#00B894",
    "warning": "#F39C12",
    "error": "#E74C3C",
    "info": "#74B9FF",
    "surface": "#FFFFFF",
    "surface_hover": "#F8F9FC",
    "surface_dim": "#F1F3F8",
    "surface_dark": "#F5F6FA",
    "text": "#2D3436",
    "text_secondary": "#636E72",
    "text_muted": "#B2BEC3",
    "border": "rgba(0,0,0,0.06)",
    "border_glass": "rgba(0,0,0,0.08)",
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
    --vh-primary: #6C5CE7;
    --vh-primary-light: #A29BFE;
    --vh-primary-dark: #5A4BD1;
    --vh-accent: #00B894;
    --vh-success: #00B894;
    --vh-warning: #F39C12;
    --vh-error: #E74C3C;
    --vh-info: #74B9FF;
    --vh-surface: #FFFFFF;
    --vh-surface-hover: #F8F9FC;
    --vh-bg: #F5F6FA;
    --vh-bg-secondary: #F1F3F8;
    --vh-text: #2D3436;
    --vh-text-secondary: #636E72;
    --vh-text-muted: #B2BEC3;
    --vh-border: rgba(0,0,0,0.06);
    --vh-border-glass: rgba(0,0,0,0.08);
    --vh-radius: 16px;
    --vh-radius-sm: 10px;
    --vh-shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.06);
    --vh-shadow-md: 0 2px 8px rgba(0,0,0,0.06), 0 4px 20px rgba(0,0,0,0.08);
    --vh-shadow-lg: 0 4px 12px rgba(0,0,0,0.08), 0 12px 32px rgba(0,0,0,0.12);
    --vh-shadow-glow: 0 0 24px rgba(108, 92, 231, 0.12);
    --vh-transition: cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after { box-sizing: border-box; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--vh-bg) !important;
    color: var(--vh-text);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Force light on Quasar/NiceGUI containers */
.q-page, .q-layout, .q-page-container, .nicegui-content {
    background: var(--vh-bg) !important;
    color: var(--vh-text) !important;
}

/* ---- Header (deep purple gradient — brand anchor) ---- */
.vh-header {
    background: linear-gradient(135deg, #6C5CE7 0%, #5A4BD1 60%, #4834B0 100%) !important;
    backdrop-filter: none !important;
    border-bottom: none !important;
    box-shadow: 0 2px 12px rgba(108, 92, 231, 0.25), 0 1px 4px rgba(0,0,0,0.1) !important;
}
.vh-header-logo {
    text-shadow: 0 1px 8px rgba(255, 255, 255, 0.25);
}

/* ---- Cards ---- */
.vh-card {
    background: var(--vh-surface) !important;
    border: 1px solid var(--vh-border) !important;
    border-radius: var(--vh-radius) !important;
    box-shadow: var(--vh-shadow-sm);
    transition: all 0.35s var(--vh-transition);
    overflow: hidden;
    position: relative;
    color: var(--vh-text) !important;
}
.vh-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--vh-text-muted);
    opacity: 0.3;
    transition: all 0.35s var(--vh-transition);
}
.vh-card:hover {
    box-shadow: var(--vh-shadow-lg);
    transform: translateY(-4px);
    border-color: var(--vh-border-glass) !important;
}
.vh-card:hover::before {
    opacity: 0.6;
}

/* Card status top-bar variants */
.vh-card-running::before {
    background: linear-gradient(90deg, #00B894, #00D4AA) !important;
    opacity: 1 !important;
    box-shadow: 0 1px 8px rgba(0, 184, 148, 0.35);
}
.vh-card-running:hover::before {
    box-shadow: 0 1px 14px rgba(0, 184, 148, 0.5);
}
.vh-card-error::before {
    background: linear-gradient(90deg, #E74C3C, #FF6B6B) !important;
    opacity: 1 !important;
    box-shadow: 0 1px 8px rgba(231, 76, 60, 0.35);
}
.vh-card-stopped::before {
    background: var(--vh-text-muted) !important;
    opacity: 0.4 !important;
}

/* ---- Buttons ---- */
.vh-btn-primary {
    background: linear-gradient(135deg, #6C5CE7 0%, #5A4BD1 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px rgba(108, 92, 231, 0.3) !important;
    transition: all 0.25s var(--vh-transition) !important;
    text-transform: none !important;
    border: 1px solid rgba(162, 155, 254, 0.3) !important;
}
.vh-btn-primary:hover {
    box-shadow: 0 6px 22px rgba(108, 92, 231, 0.45) !important;
    transform: scale(1.02);
    filter: brightness(1.08);
}

.vh-btn-accent {
    background: linear-gradient(135deg, #00B894 0%, #00A381 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(0, 184, 148, 0.3) !important;
    transition: all 0.25s var(--vh-transition) !important;
    text-transform: none !important;
}
.vh-btn-accent:hover {
    box-shadow: 0 6px 22px rgba(0, 184, 148, 0.45) !important;
    transform: scale(1.02);
    filter: brightness(1.08);
}

.vh-btn-ghost {
    border-radius: 10px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-transition) !important;
    color: var(--vh-text-secondary) !important;
}
.vh-btn-ghost:hover {
    background: rgba(108, 92, 231, 0.08) !important;
    color: var(--vh-primary) !important;
}

.vh-btn-outline {
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-transition) !important;
    color: var(--vh-text-secondary) !important;
}
.vh-btn-outline:hover {
    border-color: var(--vh-primary) !important;
    color: var(--vh-primary) !important;
    background: rgba(108, 92, 231, 0.06) !important;
}

.vh-btn-header {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-transition) !important;
}
.vh-btn-header:hover {
    background: rgba(255,255,255,0.25) !important;
    border-color: rgba(255,255,255,0.35) !important;
}

/* ---- Status Indicators ---- */
.vh-status-dot {
    width: 10px; height: 10px; border-radius: 50%; display: inline-block;
    position: relative;
    flex-shrink: 0;
}
.vh-status-dot::after {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    opacity: 0;
}
.vh-status-running {
    background: var(--vh-accent);
    box-shadow: 0 0 6px rgba(0, 184, 148, 0.5);
}
.vh-status-running::after {
    background: var(--vh-accent);
    opacity: 0.3;
    animation: statusPulse 2s ease-in-out infinite;
}
.vh-status-error {
    background: var(--vh-error);
    box-shadow: 0 0 6px rgba(231, 76, 60, 0.5);
}
.vh-status-error::after {
    background: var(--vh-error);
    opacity: 0.3;
    animation: statusPulse 2s ease-in-out infinite;
}
.vh-status-stopped {
    background: var(--vh-text-muted);
}

/* ---- Terminal Log (stays dark — natural terminal feel) ---- */
.vh-terminal {
    background: #1E1E2E !important;
    color: #CDD6F4;
    border-radius: var(--vh-radius) !important;
    font-family: 'JetBrains Mono', 'Cascadia Code', monospace !important;
    font-size: 12.5px;
    border: 1px solid rgba(0,0,0,0.1) !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.15), var(--vh-shadow-sm);
    position: relative;
}
.vh-terminal .q-virtual-scroll__content {
    padding: 16px 20px;
    line-height: 1.75;
}
.vh-terminal-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: rgba(0,0,0,0.15);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    border-radius: var(--vh-radius) var(--vh-radius) 0 0;
}
.vh-terminal-dot {
    width: 10px; height: 10px; border-radius: 50%;
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
    transition: all 0.4s var(--vh-transition);
}
.vh-step-pending .vh-step-icon {
    background: rgba(0,0,0,0.04);
    color: var(--vh-text-muted);
}
.vh-step-active .vh-step-icon {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    color: white;
    box-shadow: 0 4px 16px rgba(108, 92, 231, 0.35);
    animation: stepPulse 2s ease-in-out infinite;
}
.vh-step-done .vh-step-icon {
    background: linear-gradient(135deg, #00B894, #00D4AA);
    color: white;
    box-shadow: 0 4px 16px rgba(0, 184, 148, 0.25);
}
.vh-step-connector {
    height: 2px;
    flex: 1;
    background: rgba(0,0,0,0.06);
    margin: 0 4px;
    border-radius: 1px;
    transition: background 0.5s var(--vh-transition);
}
.vh-step-connector-done {
    background: linear-gradient(90deg, #00B894, #00D4AA) !important;
    box-shadow: 0 0 4px rgba(0, 184, 148, 0.2);
}
.vh-step-connector-active {
    background: linear-gradient(90deg, #00B894, #6C5CE7) !important;
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
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    box-shadow: 0 8px 32px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.1);
}
.vh-toast-success {
    background: rgba(0, 184, 148, 0.95);
    color: white;
    border: 1px solid rgba(0, 212, 170, 0.3);
}
.vh-toast-error {
    background: rgba(231, 76, 60, 0.95);
    color: white;
    border: 1px solid rgba(255, 107, 107, 0.3);
}
.vh-toast-info {
    background: rgba(108, 92, 231, 0.95);
    color: white;
    border: 1px solid rgba(162, 155, 254, 0.3);
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
    opacity: 0.7;
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
    border-radius: 10px !important;
    background: rgba(0,0,0,0.02) !important;
    color: var(--vh-text) !important;
}
.vh-input .q-field__label {
    color: var(--vh-text-secondary) !important;
}
.vh-input .q-field__native,
.vh-input .q-field__input {
    color: var(--vh-text) !important;
}
.vh-input .q-field__native::placeholder,
.vh-input .q-field__input::placeholder {
    color: var(--vh-text-muted) !important;
}
.vh-input .q-field--outlined .q-field__control:before {
    border-color: rgba(0,0,0,0.1) !important;
}
.vh-input .q-field--outlined .q-field__control:hover:before {
    border-color: rgba(108, 92, 231, 0.35) !important;
}
.vh-input .q-field--focused .q-field__control:after {
    border-color: var(--vh-primary) !important;
    border-width: 2px !important;
}
/* Focus glow ring */
.vh-input .q-field--focused .q-field__control {
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.12) !important;
}

/* ---- Select (for sort dropdown) ---- */
.vh-select .q-field__control {
    border-radius: 10px !important;
    background: var(--vh-surface) !important;
    color: var(--vh-text) !important;
}
.vh-select .q-field__label {
    color: var(--vh-text-secondary) !important;
}
.vh-select .q-field__native {
    color: var(--vh-text) !important;
}
.vh-select .q-field--outlined .q-field__control:before {
    border-color: rgba(0,0,0,0.1) !important;
}
.vh-select .q-field--outlined .q-field__control:hover:before {
    border-color: rgba(108, 92, 231, 0.35) !important;
}

/* ---- Empty State ---- */
.vh-empty-icon {
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(108,92,231,0.12) 0%, rgba(108,92,231,0.03) 70%);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto;
    position: relative;
}
.vh-empty-icon::after {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(108,92,231,0.06) 0%, transparent 70%);
    animation: emptyPulse 3s ease-in-out infinite;
}

/* ---- Animations ---- */
@keyframes statusPulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0; transform: scale(2); }
}
@keyframes stepPulse {
    0%, 100% { box-shadow: 0 4px 16px rgba(108, 92, 231, 0.35); }
    50% { box-shadow: 0 4px 28px rgba(108, 92, 231, 0.55); }
}
@keyframes toastIn {
    from { opacity: 0; transform: translateX(80px) scale(0.95); filter: blur(4px); }
    to { opacity: 1; transform: translateX(0) scale(1); filter: blur(0); }
}
@keyframes toastOut {
    from { opacity: 1; transform: translateX(0) scale(1); }
    to { opacity: 0; transform: translateX(80px) scale(0.9); }
}
@keyframes celebrateIn {
    from { opacity: 0; transform: scale(0.92) translateY(30px); }
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
@keyframes emptyPulse {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 0.2; transform: scale(1.15); }
}
@keyframes staggerIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.vh-fade-in {
    animation: fadeInUp 0.4s var(--vh-transition);
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }

/* ---- Badge ---- */
.vh-badge {
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.vh-badge-green {
    background: rgba(0, 184, 148, 0.1);
    color: #00956E;
}
.vh-badge-red {
    background: rgba(231, 76, 60, 0.1);
    color: #C0392B;
}
.vh-badge-grey {
    background: rgba(0,0,0,0.04);
    color: var(--vh-text-muted);
}

/* ---- Divider ---- */
.vh-divider {
    width: 100%;
    height: 1px;
    background: rgba(0,0,0,0.06);
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
    .vh-header { padding: 0 16px !important; }
    .vh-responsive-grid {
        grid-template-columns: 1fr !important;
    }
    .vh-stepper {
        padding: 16px !important;
    }
}

/* ---- Quasar overrides for light theme ---- */
.q-card {
    color: var(--vh-text) !important;
}
.q-field__control {
    color: var(--vh-text) !important;
}
.q-field__native {
    color: var(--vh-text) !important;
}
.q-expansion-item {
    color: var(--vh-text) !important;
}
.q-expansion-item .q-item {
    color: var(--vh-text) !important;
}
.q-expansion-item .q-item__label {
    color: var(--vh-text) !important;
}
.q-dialog .q-card {
    background: var(--vh-surface) !important;
    color: var(--vh-text) !important;
}
/* Quasar select dropdown menu */
.q-menu {
    background: var(--vh-surface) !important;
    color: var(--vh-text) !important;
    border: 1px solid var(--vh-border) !important;
    border-radius: 10px !important;
    box-shadow: var(--vh-shadow-md) !important;
}
.q-item {
    color: var(--vh-text) !important;
}
.q-item--active, .q-item.q-router-link--active {
    color: var(--vh-primary) !important;
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
    var colors = ['#6C5CE7','#A29BFE','#00B894','#00D4AA','#F39C12','#E74C3C','#74B9FF'];
    var rect = targetEl.getBoundingClientRect();
    var cx = rect.left + rect.width / 2;
    var cy = rect.top + rect.height / 2;

    for (var i = 0; i < 30; i++) {
        var p = document.createElement('div');
        p.className = 'vh-confetti-particle';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.left = cx + 'px';
        p.style.top = cy + 'px';
        var angle = (Math.PI * 2 * i) / 30 + (Math.random() - 0.5) * 0.5;
        var dist = 60 + Math.random() * 100;
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
    ui.dark_mode(False)
    ui.colors(primary=BRAND["primary"])
    ui.add_head_html(_FONTS_HTML)
    ui.add_head_html(_GLOBAL_CSS)
    ui.add_head_html(_TOAST_JS)
