import React from "react";

export default function Field({ label, help, control, full }) {
  return (
    <div className={`field${full ? " full" : ""}`}>
      <div>
        {label && <div className="field-label">{label}</div>}
        {help && <div className="field-help">{help}</div>}
      </div>
      <div>{control}</div>
    </div>
  );
}
