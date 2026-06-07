import React, { useState, useRef, useEffect } from "react";

export default function Tooltip({ text, children, width = 240 }) {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!visible) return undefined;

    function handle(e) {
      if (ref.current && !ref.current.contains(e.target)) setVisible(false);
    }

    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, [visible]);

  return (
    <span ref={ref} style={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
      {children}
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        style={{ marginLeft: 4, width: 14, height: 14, borderRadius: "50%", border: "1px solid var(--border-strong)", background: "var(--surface-2)", color: "var(--text-subtle)", fontSize: 9, fontWeight: 700, cursor: "pointer", lineHeight: 1, flexShrink: 0 }}
        aria-label="info"
      >
        ?
      </button>
      {visible && (
        <div style={{ position: "absolute", bottom: "calc(100% + 6px)", left: "50%", transform: "translateX(-50%)", background: "var(--surface)", border: "1px solid var(--border-strong)", borderRadius: "var(--radius)", padding: "8px 10px", fontSize: 12, lineHeight: 1.5, color: "var(--text-muted)", width, zIndex: 100, boxShadow: "var(--shadow-card)", pointerEvents: "none" }}>
          {text}
        </div>
      )}
    </span>
  );
}
