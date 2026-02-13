"""
VibeHub Design System — Dual Theme (Light/Dark)
Glassmorphism + Dynamic Glow + Breathing Animations
"""

from nicegui import ui

# ---- Design Tokens (Dark Theme - for Python reference) ----
BRAND = {
    "primary": "#818cf8",
    "primary_light": "#a5b4fc",
    "primary_dark": "#6366f1",
    "accent": "#34d399",
    "success": "#34d399",
    "warning": "#fbbf24",
    "error": "#f87171",
    "info": "#60a5fa",
    "surface": "#27272a",
    "surface_hover": "#3f3f46",
    "surface_dim": "#18181b",
    "surface_dark": "#09090b",
    "text": "#fafafa",
    "text_secondary": "#a1a1aa",
    "text_muted": "#71717a",
    "border": "rgba(255,255,255,0.06)",
    "border_glass": "rgba(255,255,255,0.08)",
}

# ---- Light Theme Tokens (for Python reference) ----
BRAND_LIGHT = {
    "primary": "#4F46E5",
    "primary_light": "#818CF8",
    "primary_dark": "#3730A3",
    "accent": "#059669",
    "success": "#059669",
    "warning": "#D97706",
    "error": "#DC2626",
    "info": "#2563EB",
    "surface": "#FFFFFF",
    "surface_hover": "#F8FAFC",
    "bg": "#F8FAFC",
    "bg_secondary": "#F1F5F9",
    "text": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    "border": "rgba(0,0,0,0.06)",
    "border_card": "#E2E8F0",
}

# ---- Google Fonts (with Geist) ----
_FONTS_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-sans/style.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/geist@1.3.1/dist/fonts/geist-mono/style.min.css">
"""

# ---- FOUC Prevention Script (must be injected first) ----
_THEME_INIT_JS = """
<script>
(function(){
    var t = localStorage.getItem('vh-theme') || 'light';
    document.documentElement.dataset.theme = t;
})();
</script>
"""

# ---- Global CSS (Dual Theme Variables + Base + Components) ----
_GLOBAL_CSS = """
<style>
/* === Public Tokens (theme-independent) === */
:root {
    --vh-radius: 16px;
    --vh-radius-sm: 10px;
    --vh-radius-lg: 20px;
    --vh-transition: cubic-bezier(0.4, 0, 0.2, 1);
    --vh-ease-out-back: cubic-bezier(0.16, 1, 0.3, 1);
    --vh-ease-snappy: cubic-bezier(0.25, 0.1, 0.25, 1);
    --vh-font-sans: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --vh-font-mono: 'JetBrains Mono', 'Geist Mono', monospace;
}

/* === Light Theme (Linear.app Minimalist) === */
[data-theme="light"] {
    --vh-primary: #4F46E5;
    --vh-primary-light: #818CF8;
    --vh-primary-dark: #3730A3;
    --vh-accent: #059669;
    --vh-success: #059669;
    --vh-warning: #D97706;
    --vh-error: #DC2626;
    --vh-info: #2563EB;
    --vh-surface: #FFFFFF;
    --vh-surface-hover: #FAFAFA;
    --vh-bg: #FBFBFB;
    --vh-bg-secondary: #F5F5F5;
    --vh-text: #18181B;
    --vh-text-secondary: #52525B;
    --vh-text-muted: #A1A1AA;
    --vh-border: rgba(0, 0, 0, 0.05);
    --vh-border-glass: rgba(0, 0, 0, 0.05);
    --vh-border-card: rgba(0, 0, 0, 0.06);
    --vh-glass-bg: rgba(255, 255, 255, 0.85);
    --vh-glass-border: rgba(0, 0, 0, 0.05);
    --vh-glass-blur: blur(20px) saturate(150%);
    /* Linear-style: no heavy shadows, use subtle inner glow */
    --vh-shadow-sm: none;
    --vh-shadow-md: none;
    --vh-shadow-lg: 0 1px 3px rgba(0,0,0,0.04);
    --vh-shadow-xl: 0 2px 8px rgba(0,0,0,0.06);
    --vh-shadow-glow: 0 0 0 3px rgba(79,70,229,0.08);
    /* Inner glow for premium feel */
    --vh-inner-glow: inset 0 1px 0 0 rgba(255,255,255,0.8);
    --vh-success-bg: #ECFDF5;
    --vh-warning-bg: #FFFBEB;
    --vh-error-bg: #FEF2F2;
    --vh-info-bg: #EFF6FF;
}

/* === Dark Theme === */
[data-theme="dark"] {
    --vh-primary: #818cf8;
    --vh-primary-light: #a5b4fc;
    --vh-primary-dark: #6366f1;
    --vh-accent: #34d399;
    --vh-success: #34d399;
    --vh-warning: #fbbf24;
    --vh-error: #f87171;
    --vh-info: #60a5fa;
    --vh-surface: #27272a;
    --vh-surface-hover: #3f3f46;
    --vh-bg: #09090b;
    --vh-bg-secondary: #18181b;
    --vh-text: #fafafa;
    --vh-text-secondary: #a1a1aa;
    --vh-text-muted: #71717a;
    --vh-border: rgba(255,255,255,0.06);
    --vh-border-glass: rgba(255,255,255,0.08);
    --vh-border-card: rgba(255,255,255,0.08);
    --vh-glass-bg: rgba(39, 39, 42, 0.6);
    --vh-glass-border: rgba(255, 255, 255, 0.08);
    --vh-glass-blur: blur(16px) saturate(180%);
    --vh-shadow-sm: 0 1px 3px rgba(0,0,0,0.3), 0 2px 8px rgba(0,0,0,0.2);
    --vh-shadow-md: 0 2px 8px rgba(0,0,0,0.3), 0 4px 20px rgba(0,0,0,0.25);
    --vh-shadow-lg: 0 4px 12px rgba(0,0,0,0.3), 0 12px 32px rgba(0,0,0,0.4);
    --vh-shadow-xl: 0 8px 24px rgba(0,0,0,0.4), 0 32px 64px rgba(0,0,0,0.5);
    --vh-shadow-glow: 0 0 24px rgba(129, 140, 248, 0.15);
    --vh-success-bg: rgba(52, 211, 153, 0.15);
    --vh-warning-bg: rgba(251, 191, 36, 0.15);
    --vh-error-bg: rgba(248, 113, 113, 0.15);
    --vh-info-bg: rgba(96, 165, 250, 0.15);
}

*, *::before, *::after { box-sizing: border-box; }

body {
    font-family: var(--vh-font-sans) !important;
    background: var(--vh-bg) !important;
    color: var(--vh-text);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: -0.011em;
}

/* Typography: Linear-style tight letter-spacing */
h1, h2, h3, .vh-title, .text-2xl, .text-xl, .text-lg {
    letter-spacing: -0.02em;
    font-weight: 600;
}
.font-semibold, .font-bold {
    letter-spacing: -0.02em;
}

/* Force theme colors on Quasar/NiceGUI containers */
.q-page, .q-layout, .q-page-container, .nicegui-content {
    background: var(--vh-bg) !important;
    color: var(--vh-text) !important;
}

/* ---- Header (theme-aware) ---- */
.vh-header {
    background: var(--vh-glass-bg) !important;
    backdrop-filter: var(--vh-glass-blur) !important;
    -webkit-backdrop-filter: var(--vh-glass-blur) !important;
    border-bottom: 1px solid var(--vh-border) !important;
    box-shadow: var(--vh-shadow-sm) !important;
    transition: background 0.3s ease, border-color 0.3s ease;
}
[data-theme="dark"] .vh-header {
    background: rgba(9, 9, 11, 0.8) !important;
    border-bottom: 1px solid transparent !important;
    border-image: linear-gradient(90deg, transparent, rgba(129,140,248,0.4), transparent) 1 !important;
    box-shadow: 0 1px 24px rgba(0,0,0,0.4) !important;
}
.vh-header-logo {
    color: var(--vh-text) !important;
    transition: color 0.3s ease, text-shadow 0.3s ease;
}
[data-theme="dark"] .vh-header-logo {
    color: #FFFFFF !important;
    text-shadow: 0 0 12px rgba(129, 140, 248, 0.4);
}
[data-theme="light"] .vh-header-logo {
    text-shadow: none;
}

/* ---- Cards (theme-aware glass + inner border + dynamic glow) ---- */
.vh-card {
    background: var(--vh-glass-bg) !important;
    backdrop-filter: var(--vh-glass-blur) !important;
    -webkit-backdrop-filter: var(--vh-glass-blur) !important;
    border: none !important;
    border-radius: var(--vh-radius) !important;
    box-shadow: inset 0 0 0 1px var(--vh-glass-border), var(--vh-shadow-sm);
    transition: transform 0.35s var(--vh-transition), box-shadow 0.35s var(--vh-transition), background 0.3s ease;
    overflow: hidden;
    position: relative;
    color: var(--vh-text) !important;
}
/* Linear.app style: no shadow, thin border + inner glow */
[data-theme="light"] .vh-card {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    box-shadow: var(--vh-inner-glow) !important;
    backdrop-filter: none !important;
}
.vh-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--vh-text-muted);
    opacity: 0.3;
    transition: all 0.35s var(--vh-transition);
}
[data-theme="light"] .vh-card::before {
    height: 3px;
    opacity: 0;
}
/* Mouse-follow glow layer */
.vh-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: radial-gradient(
        600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
        rgba(129, 140, 248, 0.08),
        transparent 40%
    );
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
    z-index: 1;
}
[data-theme="light"] .vh-card::after {
    background: radial-gradient(
        600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
        rgba(79, 70, 229, 0.03),
        transparent 40%
    );
}
.vh-card:hover {
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12), var(--vh-shadow-lg), 0 0 24px rgba(129,140,248,0.06);
    transform: translateY(-4px);
}
/* Linear-style hover: subtle border darken + micro lift */
[data-theme="light"] .vh-card:hover {
    border-color: rgba(0, 0, 0, 0.08) !important;
    box-shadow: var(--vh-inner-glow), 0 2px 8px rgba(0,0,0,0.04) !important;
    transform: translateY(-2px);
}
.vh-card:hover::before { opacity: 0.8; }
.vh-card:hover::after { opacity: 1; }

/* Card status top-bar variants */
.vh-card-running::before {
    background: linear-gradient(90deg, #34d399, #6ee7b7) !important;
    opacity: 1 !important;
    box-shadow: 0 0 12px rgba(52, 211, 153, 0.4);
}
[data-theme="light"] .vh-card-running {
    background: #FFFFFF !important;
    border-color: rgba(5, 150, 105, 0.12) !important;
}
[data-theme="light"] .vh-card-running::before {
    background: linear-gradient(90deg, #059669, #34D399) !important;
    opacity: 1 !important;
    height: 3px;
}
.vh-card-running:hover::before {
    box-shadow: 0 0 20px rgba(52, 211, 153, 0.6);
}
.vh-card-error::before {
    background: linear-gradient(90deg, #f87171, #fca5a5) !important;
    opacity: 1 !important;
    box-shadow: 0 0 12px rgba(248, 113, 113, 0.4);
}
[data-theme="light"] .vh-card-error {
    background: #FFFFFF !important;
    border-color: rgba(220, 38, 38, 0.10) !important;
}
[data-theme="light"] .vh-card-error::before {
    background: linear-gradient(90deg, #DC2626, #F87171) !important;
    opacity: 1 !important;
    height: 3px;
}
.vh-card-stopped::before {
    background: var(--vh-text-muted) !important;
    opacity: 0.3 !important;
}
[data-theme="light"] .vh-card-stopped::before {
    opacity: 0 !important;
}

/* ---- Buttons (theme-aware, Linear-style) ---- */
.vh-btn-primary {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
    color: white !important;
    border-radius: var(--vh-radius-sm) !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    transition: all 0.2s var(--vh-ease-snappy) !important;
    text-transform: none !important;
    border: 1px solid rgba(165, 180, 252, 0.2) !important;
}
/* Linear-style: solid color, no gradient, subtle shadow */
[data-theme="light"] .vh-btn-primary {
    background: #4F46E5 !important;
    box-shadow: none !important;
    border: none !important;
}
.vh-btn-primary:hover {
    box-shadow: 0 6px 22px rgba(99, 102, 241, 0.5) !important;
    transform: scale(1.02);
    filter: brightness(1.1);
}
[data-theme="light"] .vh-btn-primary:hover {
    background: #4338CA !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2) !important;
    transform: translateY(-1px);
    filter: none;
}
.vh-btn-accent {
    background: linear-gradient(135deg, #059669 0%, #34d399 100%) !important;
    color: white !important;
    border-radius: var(--vh-radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(52, 211, 153, 0.3) !important;
    transition: all 0.2s var(--vh-ease-snappy) !important;
    text-transform: none !important;
}
[data-theme="light"] .vh-btn-accent {
    background: #059669 !important;
    box-shadow: none !important;
}
.vh-btn-accent:hover {
    box-shadow: 0 6px 22px rgba(52, 211, 153, 0.45) !important;
    transform: scale(1.02);
    filter: brightness(1.1);
}
[data-theme="light"] .vh-btn-accent:hover {
    background: #047857 !important;
    box-shadow: 0 2px 8px rgba(5, 150, 105, 0.2) !important;
    transform: translateY(-1px);
    filter: none;
}
.vh-btn-ghost {
    border-radius: var(--vh-radius-sm) !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-ease-snappy) !important;
    color: var(--vh-text-secondary) !important;
}
.vh-btn-ghost:hover {
    background: rgba(129, 140, 248, 0.1) !important;
    color: var(--vh-primary) !important;
}
[data-theme="light"] .vh-btn-ghost:hover {
    background: rgba(0, 0, 0, 0.04) !important;
    color: var(--vh-text) !important;
}
.vh-btn-outline {
    border: 1.5px solid var(--vh-border) !important;
    border-radius: var(--vh-radius-sm) !important;
    font-weight: 500 !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-ease-snappy) !important;
    color: var(--vh-text-secondary) !important;
}
[data-theme="dark"] .vh-btn-outline {
    border-color: rgba(255,255,255,0.12) !important;
}
[data-theme="light"] .vh-btn-outline {
    border-color: rgba(0, 0, 0, 0.08) !important;
}
.vh-btn-outline:hover {
    border-color: var(--vh-primary) !important;
    color: var(--vh-primary) !important;
    background: rgba(129, 140, 248, 0.08) !important;
}
[data-theme="light"] .vh-btn-outline:hover {
    border-color: rgba(0, 0, 0, 0.15) !important;
    color: var(--vh-text) !important;
    background: rgba(0, 0, 0, 0.02) !important;
}
.vh-btn-header {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    font-weight: 600 !important;
    border-radius: var(--vh-radius-sm) !important;
    text-transform: none !important;
    transition: all 0.2s var(--vh-ease-snappy) !important;
}
[data-theme="light"] .vh-btn-header {
    background: var(--vh-primary) !important;
    color: white !important;
    border: none !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}
.vh-btn-header:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.25) !important;
    box-shadow: 0 0 16px rgba(129, 140, 248, 0.15) !important;
}
[data-theme="light"] .vh-btn-header:hover {
    background: #4338CA !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.15) !important;
}

/* ---- Status Indicators ---- */
.vh-status-dot {
    width: 10px; height: 10px; border-radius: 50%; display: inline-block;
    position: relative; flex-shrink: 0;
}
.vh-status-dot::after {
    content: '';
    position: absolute; inset: -3px; border-radius: 50%; opacity: 0;
}
.vh-status-running {
    background: var(--vh-accent);
    box-shadow: 0 0 8px rgba(52, 211, 153, 0.6);
}
.vh-status-running::after {
    background: var(--vh-accent); opacity: 0.3;
    animation: statusPulse 2s ease-in-out infinite;
}
.vh-status-error {
    background: var(--vh-error);
    box-shadow: 0 0 8px rgba(248, 113, 113, 0.6);
}
.vh-status-error::after {
    background: var(--vh-error); opacity: 0.3;
    animation: statusPulse 2s ease-in-out infinite;
}
.vh-status-stopped { background: var(--vh-text-muted); }

/* ---- Terminal Log (theme-aware) ---- */
.vh-terminal {
    background: #0c0c0f !important;
    color: #e4e4e7;
    border-radius: var(--vh-radius) !important;
    font-family: var(--vh-font-mono) !important;
    font-size: 13px;
    border: none !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06), inset 0 2px 12px rgba(0,0,0,0.4), 0 8px 32px rgba(0,0,0,0.3);
    position: relative;
}
[data-theme="light"] .vh-terminal {
    background: #F4F4F5 !important;
    color: #3F3F46 !important;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06),
                inset 0 2px 4px rgba(0, 0, 0, 0.02),
                var(--vh-shadow-sm) !important;
}
.vh-terminal .q-virtual-scroll__content {
    padding: 16px 20px; line-height: 1.8;
}
.vh-terminal-header {
    display: flex; align-items: center; gap: 8px;
    padding: 12px 16px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    border-radius: var(--vh-radius) var(--vh-radius) 0 0;
}
[data-theme="light"] .vh-terminal-header {
    background: rgba(0, 0, 0, 0.02) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
}
.vh-terminal-dot { width: 10px; height: 10px; border-radius: 50%; }
.vh-terminal-title {
    color: rgba(255,255,255,0.5);
}
[data-theme="light"] .vh-terminal-title {
    color: var(--vh-text-muted) !important;
}

/* ---- Progress Stepper (theme-aware breathing glow) ---- */
.vh-stepper {
    background: var(--vh-glass-bg);
    backdrop-filter: var(--vh-glass-blur);
    -webkit-backdrop-filter: var(--vh-glass-blur);
    box-shadow: inset 0 0 0 1px var(--vh-glass-border);
    border: none; border-radius: var(--vh-radius) !important;
    padding: 20px 28px;
}
[data-theme="light"] .vh-stepper {
    background: rgba(255, 255, 255, 0.80) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04),
                var(--vh-shadow-sm) !important;
}
.vh-step-icon {
    width: 40px; height: 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; transition: all 0.4s var(--vh-transition);
}
.vh-step-pending .vh-step-icon {
    background: rgba(255,255,255,0.05); color: var(--vh-text-muted);
}
[data-theme="light"] .vh-step-pending .vh-step-icon {
    background: rgba(0, 0, 0, 0.04);
    color: var(--vh-text-muted);
}
.vh-step-active .vh-step-icon {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    color: white;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
    animation: stepBreathe 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
[data-theme="light"] .vh-step-active .vh-step-icon {
    background: linear-gradient(135deg, #4F46E5, #6366F1);
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25);
    animation: stepBreatheLight 2.5s ease-in-out infinite;
}
.vh-step-done .vh-step-icon {
    background: linear-gradient(135deg, #059669, #34d399);
    color: white;
    box-shadow: 0 4px 16px rgba(52, 211, 153, 0.3);
}
.vh-step-connector {
    height: 2px; flex: 1; background: rgba(255,255,255,0.06);
    margin: 0 4px; border-radius: 1px;
    transition: background 0.5s var(--vh-transition);
}
[data-theme="light"] .vh-step-connector {
    background: rgba(0, 0, 0, 0.06);
}
.vh-step-connector-done {
    background: linear-gradient(90deg, #059669, #34d399) !important;
    box-shadow: 0 0 6px rgba(52, 211, 153, 0.25);
}
.vh-step-connector-active {
    background: linear-gradient(90deg, #34d399, #6366f1) !important;
}

/* ---- Input (theme-aware) ---- */
.vh-input .q-field__control {
    border-radius: var(--vh-radius-sm) !important;
    background: rgba(255,255,255,0.04) !important;
    color: var(--vh-text) !important;
}
[data-theme="light"] .vh-input .q-field__control {
    background: rgba(0, 0, 0, 0.02) !important;
}
.vh-input .q-field__label { color: var(--vh-text-secondary) !important; }
.vh-input .q-field__native,
.vh-input .q-field__input { color: var(--vh-text) !important; }
.vh-input .q-field__native::placeholder,
.vh-input .q-field__input::placeholder { color: var(--vh-text-muted) !important; }
.vh-input .q-field--outlined .q-field__control:before {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-theme="light"] .vh-input .q-field--outlined .q-field__control:before {
    border-color: #E2E8F0 !important;
}
.vh-input .q-field--outlined .q-field__control:hover:before {
    border-color: rgba(129, 140, 248, 0.35) !important;
}
[data-theme="light"] .vh-input .q-field--outlined .q-field__control:hover:before {
    border-color: rgba(79, 70, 229, 0.35) !important;
}
.vh-input .q-field--focused .q-field__control:after {
    border-color: var(--vh-primary) !important; border-width: 2px !important;
}
.vh-input .q-field--focused .q-field__control {
    box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.5), 0 0 0 3px rgba(129, 140, 248, 0.1) !important;
}
[data-theme="light"] .vh-input .q-field--focused .q-field__control {
    box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.5),
                0 0 0 3px rgba(79, 70, 229, 0.08) !important;
}

/* ---- Select (theme-aware) ---- */
.vh-select .q-field__control {
    border-radius: var(--vh-radius-sm) !important;
    background: rgba(255,255,255,0.04) !important;
    color: var(--vh-text) !important;
}
[data-theme="light"] .vh-select .q-field__control {
    background: rgba(0, 0, 0, 0.02) !important;
}
.vh-select .q-field__label { color: var(--vh-text-secondary) !important; }
.vh-select .q-field__native { color: var(--vh-text) !important; }
.vh-select .q-field--outlined .q-field__control:before {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-theme="light"] .vh-select .q-field--outlined .q-field__control:before {
    border-color: #E2E8F0 !important;
}
.vh-select .q-field--outlined .q-field__control:hover:before {
    border-color: rgba(129, 140, 248, 0.35) !important;
}

/* ---- Toast (theme-aware) ---- */
.vh-toast-container {
    position: fixed; top: 80px; right: 24px; z-index: 9999;
    display: flex; flex-direction: column; gap: 12px; pointer-events: none;
}
.vh-toast {
    pointer-events: auto; min-width: 360px; max-width: 440px;
    padding: 16px 20px; border-radius: 14px;
    display: flex; align-items: flex-start; gap: 14px;
    animation: toastIn 0.4s var(--vh-ease-out-back);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3);
}
[data-theme="light"] .vh-toast {
    box-shadow: var(--vh-shadow-xl) !important;
}
.vh-toast-success {
    background: rgba(5, 150, 105, 0.92); color: white;
    border: 1px solid rgba(52, 211, 153, 0.3);
}
.vh-toast-error {
    background: rgba(220, 38, 38, 0.92); color: white;
    border: 1px solid rgba(248, 113, 113, 0.3);
}
.vh-toast-info {
    background: rgba(99, 102, 241, 0.92); color: white;
    border: 1px solid rgba(165, 180, 252, 0.3);
}
.vh-toast-icon { font-size: 24px; flex-shrink: 0; margin-top: 1px; }
.vh-toast-body { flex: 1; }
.vh-toast-title { font-weight: 700; font-size: 15px; margin-bottom: 2px; }
.vh-toast-msg { font-size: 13px; opacity: 0.9; }
.vh-toast-close {
    cursor: pointer; opacity: 0.7; transition: opacity 0.2s;
    font-size: 18px; flex-shrink: 0; margin-top: 1px;
}
.vh-toast-close:hover { opacity: 1; }
.vh-toast-exit { animation: toastOut 0.35s cubic-bezier(0.4, 0, 1, 1) forwards; }

/* ---- Success Celebration (theme-aware) ---- */
.vh-celebrate { animation: celebrateIn 0.6s var(--vh-ease-out-back); }
[data-theme="light"] .vh-celebrate .q-card,
[data-theme="light"] .vh-celebrate-card {
    background: linear-gradient(135deg, #F0FDF9 0%, #FFFFFF 100%) !important;
    box-shadow: inset 0 0 0 1px rgba(5, 150, 105, 0.1),
                var(--vh-shadow-lg) !important;
}
.vh-celebrate-icon {
    animation: celebrateBounce 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s both;
}
.vh-confetti-particle {
    position: absolute; width: 8px; height: 8px; border-radius: 2px;
    animation: confettiFall 1.5s var(--vh-transition) forwards;
    pointer-events: none;
}

/* ---- Empty State (theme-aware) ---- */
.vh-empty-icon {
    width: 140px; height: 140px; border-radius: 50%;
    background: radial-gradient(circle, rgba(129,140,248,0.15) 0%, rgba(139,92,246,0.05) 50%, transparent 70%);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto; position: relative;
    box-shadow: 0 0 60px rgba(129, 140, 248, 0.1);
}
[data-theme="light"] .vh-empty-icon {
    background: radial-gradient(circle, rgba(79,70,229,0.08) 0%, rgba(79,70,229,0.02) 50%, transparent 70%);
    box-shadow: 0 0 40px rgba(79, 70, 229, 0.05);
}
.vh-empty-icon::after {
    content: ''; position: absolute; inset: -10px; border-radius: 50%;
    background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
    animation: emptyPulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* ---- Badge (theme-aware) ---- */
.vh-badge {
    padding: 3px 10px; border-radius: 6px;
    font-size: 12px; font-weight: 600; letter-spacing: 0.02em;
}
.vh-badge-green {
    background: rgba(52, 211, 153, 0.15); color: #6ee7b7;
}
[data-theme="light"] .vh-badge-green {
    background: #D1FAE5; color: #059669;
}
.vh-badge-red {
    background: rgba(248, 113, 113, 0.15); color: #fca5a5;
}
[data-theme="light"] .vh-badge-red {
    background: #FEE2E2; color: #DC2626;
}
.vh-badge-grey {
    background: rgba(255,255,255,0.06); color: var(--vh-text-muted);
}
[data-theme="light"] .vh-badge-grey {
    background: #F1F5F9; color: var(--vh-text-muted);
}

/* ---- Divider (theme-aware) ---- */
.vh-divider {
    width: 100%; height: 1px;
    background: var(--vh-border);
}

/* ---- Animations ---- */
@keyframes statusPulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0; transform: scale(2); }
}
@keyframes stepBreathe {
    0%, 100% {
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4), 0 0 0 0 rgba(129, 140, 248, 0.3);
    }
    50% {
        box-shadow: 0 4px 28px rgba(99, 102, 241, 0.6), 0 0 0 8px rgba(129, 140, 248, 0);
    }
}
@keyframes stepBreatheLight {
    0%, 100% {
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25),
                    0 0 0 0 rgba(79, 70, 229, 0.15);
    }
    50% {
        box-shadow: 0 2px 12px rgba(79, 70, 229, 0.35),
                    0 0 0 6px rgba(79, 70, 229, 0);
    }
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
.vh-fade-in { animation: fadeInUp 0.4s var(--vh-transition); }

/* ---- Scrollbar (theme-aware) ---- */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
[data-theme="light"] ::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
}
[data-theme="light"] ::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.2);
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
    .vh-header { padding: 0 16px !important; }
    .vh-responsive-grid { grid-template-columns: 1fr !important; }
    .vh-stepper { padding: 16px !important; }
}

/* ---- Quasar overrides (theme-aware) ---- */
.q-card { color: var(--vh-text) !important; background: transparent !important; }
.q-field__control { color: var(--vh-text) !important; }
.q-field__native { color: var(--vh-text) !important; }
.q-expansion-item { color: var(--vh-text) !important; }
.q-expansion-item .q-item { color: var(--vh-text) !important; }
.q-expansion-item .q-item__label { color: var(--vh-text) !important; }
.q-dialog .q-card {
    background: var(--vh-surface) !important;
    color: var(--vh-text) !important;
    box-shadow: inset 0 0 0 1px var(--vh-glass-border), var(--vh-shadow-xl) !important;
    border-radius: var(--vh-radius) !important;
}
[data-theme="light"] .q-dialog .q-card {
    background: #FFFFFF !important;
    box-shadow: var(--vh-shadow-xl) !important;
}
.q-menu {
    background: var(--vh-surface) !important;
    color: var(--vh-text) !important;
    border: 1px solid var(--vh-border-card) !important;
    border-radius: var(--vh-radius-sm) !important;
    box-shadow: var(--vh-shadow-lg) !important;
}
[data-theme="light"] .q-menu {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}
.q-item { color: var(--vh-text) !important; }
.q-item--active, .q-item.q-router-link--active { color: var(--vh-primary) !important; }
.q-item:hover { background: rgba(255,255,255,0.05) !important; }
[data-theme="light"] .q-item:hover {
    background: rgba(0, 0, 0, 0.03) !important;
}

/* backdrop-filter fallback for unsupported browsers */
@supports not (backdrop-filter: blur(1px)) {
    .vh-card { background: rgba(39, 39, 42, 0.95) !important; }
    .vh-header { background: rgba(9, 9, 11, 0.95) !important; }
    .vh-stepper { background: rgba(39, 39, 42, 0.95) !important; }
    .vh-toast { backdrop-filter: none !important; }
    [data-theme="light"] .vh-card { background: #FFFFFF !important; }
    [data-theme="light"] .vh-header { background: rgba(255, 255, 255, 0.95) !important; }
    [data-theme="light"] .vh-stepper { background: rgba(255, 255, 255, 0.95) !important; }
}
</style>
"""

# ---- Toast + Confetti + Dynamic Glow + Theme Toggle JS ----
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

// Confetti burst
function vhConfetti(targetEl) {
    var colors = ['#818cf8','#a5b4fc','#34d399','#6ee7b7','#fbbf24','#f87171','#60a5fa','#c084fc'];
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

// Theme toggle
window.vhToggleTheme = function() {
    var current = document.documentElement.dataset.theme;
    var next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('vh-theme', next);

    // Update toggle button icon
    var btn = document.querySelector('.vh-theme-toggle .material-icons');
    if (btn) {
        btn.textContent = next === 'dark' ? 'light_mode' : 'dark_mode';
    }

    // Smooth transition
    document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(function() {
        document.documentElement.style.transition = '';
    }, 300);
};

window.vhGetTheme = function() {
    return document.documentElement.dataset.theme || 'light';
};

// Dynamic glow: auto-bind mousemove on .vh-card via MutationObserver
(function() {
    function bindGlow(card) {
        if (card.__vhGlow) return;
        card.__vhGlow = true;
        card.addEventListener('mousemove', function(e) {
            var rect = card.getBoundingClientRect();
            card.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
            card.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
        });
    }
    function scanCards() {
        document.querySelectorAll('.vh-card').forEach(bindGlow);
    }
    // Initial scan
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scanCards);
    } else {
        scanCards();
    }
    // Watch for dynamically added cards
    var obs = new MutationObserver(function(mutations) {
        var found = false;
        for (var i = 0; i < mutations.length; i++) {
            if (mutations[i].addedNodes.length) { found = true; break; }
        }
        if (found) requestAnimationFrame(scanCards);
    });
    obs.observe(document.body, { childList: true, subtree: true });
})();
</script>
"""


def apply_theme(mode: str = "light"):
    """
    Inject the VibeHub design system.

    Args:
        mode: "light" or "dark", defaults to "light"
    """
    # FOUC prevention: inject theme init script first
    ui.add_head_html(_THEME_INIT_JS)

    # Quasar dark mode control (None = auto, let CSS handle it)
    ui.dark_mode(None)

    # Set Quasar primary color based on mode
    primary = BRAND_LIGHT["primary"] if mode == "light" else BRAND["primary"]
    ui.colors(primary=primary)

    # Inject fonts (with Geist)
    ui.add_head_html(_FONTS_HTML)

    # Inject dual-theme CSS + component styles
    ui.add_head_html(_GLOBAL_CSS)

    # Inject JS (Toast + Confetti + Glow + Theme Toggle)
    ui.add_head_html(_TOAST_JS)

    # Set initial theme from localStorage or default
    ui.run_javascript(f"""
        var saved = localStorage.getItem('vh-theme') || '{mode}';
        document.documentElement.dataset.theme = saved;
    """)
