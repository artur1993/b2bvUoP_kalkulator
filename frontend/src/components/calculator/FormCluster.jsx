import React from "react";

export default function FormCluster({ badge, badgeClass, title, sub, children }) {
  return (
    <div className="cluster">
      {(badge || title) && (
        <div className="cluster-head">
          {badge && <span className={`badge ${badgeClass || ""}`}>{badge}</span>}
          <div>
            {title && <div className="cluster-title">{title}</div>}
            {sub && <div className="cluster-sub">{sub}</div>}
          </div>
        </div>
      )}
      {children}
    </div>
  );
}

export function SubsecTitle({ children }) {
  return <div className="subsec-title">{children}</div>;
}
