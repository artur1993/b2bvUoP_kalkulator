import React from "react";

export default function Field({ label, help, control, full }) {
  const labelledControl =
    label && React.isValidElement(control)
      ? React.cloneElement(control, {
          "aria-label": control.props["aria-label"] ?? label,
        })
      : control;

  return (
    <div className={`field${full ? " full" : ""}`}>
      <div>
        {label && <div className="field-label">{label}</div>}
        {help && <div className="field-help">{help}</div>}
      </div>
      <div>{labelledControl}</div>
    </div>
  );
}
