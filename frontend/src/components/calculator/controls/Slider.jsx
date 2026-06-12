import React from "react";

export default function Slider({ value, onChange, min = 0, max = 100, step = 1, suffix = "", "aria-label": ariaLabel }) {
  return (
    <div className="slider-wrap">
      <input
        type="range"
        className="slider-input"
        value={value}
        min={min}
        max={max}
        step={step}
        aria-label={ariaLabel}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <span className="slider-value">{value}{suffix}</span>
    </div>
  );
}
