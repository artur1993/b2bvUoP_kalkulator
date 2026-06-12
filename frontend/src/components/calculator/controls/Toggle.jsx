import React from "react";

export default function Toggle({ value, onChange, "aria-label": ariaLabel, "aria-labelledby": ariaLabelledby }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={value}
      aria-label={ariaLabel}
      aria-labelledby={!ariaLabel ? ariaLabelledby : undefined}
      className={`toggle${value ? " on" : ""}`}
      onClick={() => onChange(!value)}
    />
  );
}
