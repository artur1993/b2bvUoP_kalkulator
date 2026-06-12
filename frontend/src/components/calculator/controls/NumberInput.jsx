import React from "react";

export default function NumberInput({ value, onChange, suffix, min, max, step = 1, "data-testid": testId }) {
  return (
    <div className="number-input-wrap">
      <input
        type="number"
        className="number-input"
        value={value}
        min={min}
        max={max}
        step={step}
        data-testid={testId}
        onChange={(e) => {
          const v = parseFloat(e.target.value);
          if (!isNaN(v)) onChange(v);
        }}
      />
      {suffix && <span className="number-input-suffix">{suffix}</span>}
    </div>
  );
}
