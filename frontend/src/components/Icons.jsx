/**
 * Inline SVG icon system — no external dependency needed.
 * All icons are 24×24 viewBox, stroke-based (Lucide-compatible style).
 */
const icon = (d, extra = "") => ({ size = 20, className = "", style = {}, strokeWidth = 1.75 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    style={style}
  >
    {typeof d === "string" ? <path d={d} /> : d}
    {extra && <path d={extra} />}
  </svg>
);

const multi = (children) => ({ size = 20, className = "", style = {}, strokeWidth = 1.75 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    style={style}
  >
    {children}
  </svg>
);

export const Zap = multi(<><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></>);
export const Sun = multi(<><circle cx="12" cy="12" r="5" /><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" /></>);
export const Moon = icon("M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z");
export const ArrowLeft = icon("M19 12H5M12 19l-7-7 7-7");
