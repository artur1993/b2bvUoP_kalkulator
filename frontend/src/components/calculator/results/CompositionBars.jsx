import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

function BarSegment({ kind, val, total }) {
  const pct = total > 0 ? Math.max(0, val / total) : 0;
  if (pct < 0.001) return null;
  const showLabel = pct > 0.06;
  return (
    <div className={`bar-seg ${kind}`} style={{ flexGrow: pct, flexBasis: 0 }}>
      {showLabel && <span>{Math.round(pct * 100)}%</span>}
    </div>
  );
}

export default function CompositionBars({ result }) {
  const { t } = useTranslation();
  const { b2b, uop } = result;

  const b2bTotal = b2b.gross + b2b.lostRevenue;
  const uopTotal = uop.gross + uop.benefits;

  const b2bSegments = [
    { kind: "net", val: b2b.net },
    { kind: "zus", val: b2b.zusSocial + b2b.zusHealth },
    { kind: "tax", val: b2b.tax },
    { kind: "costs", val: b2b.costs },
    { kind: "lost", val: b2b.lostRevenue },
  ];

  const uopSegments = [
    { kind: "net", val: uop.net },
    { kind: "zus", val: uop.zusSocial + uop.zusHealth },
    { kind: "tax", val: uop.tax },
    { kind: "benefits", val: uop.benefits },
  ];

  return (
    <div className="composition" data-testid="composition-bars">
      <div className="composition-head">
        <h4>{t("res.composition_title") || "Gdzie idzie każda złotówka"}</h4>
        <span>{t("res.composition_sub") || "Rozkład rocznego przychodu"}</span>
      </div>

      <div className="comp-row">
        <div className="comp-label">
          <div className="name">
            <span className="badge b2b">B2B</span>
          </div>
          <span className="total">{fmt(b2bTotal)}</span>
        </div>
        <div className="comp-bar">
          {b2bSegments.map((s, i) => (
            <BarSegment key={i} kind={s.kind} val={s.val} total={b2bTotal} />
          ))}
        </div>
      </div>

      <div className="comp-row">
        <div className="comp-label">
          <div className="name">
            <span className="badge uop">UoP</span>
          </div>
          <span className="total">{fmt(uopTotal)}</span>
        </div>
        <div className="comp-bar">
          {uopSegments.map((s, i) => (
            <BarSegment key={i} kind={s.kind} val={s.val} total={uopTotal} />
          ))}
        </div>
      </div>

      <div className="comp-legend">
        {[
          { kind: "net", label: t("res.legend.net") || "Netto" },
          { kind: "zus", label: t("res.legend.zus") || "ZUS" },
          { kind: "tax", label: t("res.legend.tax") || "Podatek" },
          { kind: "costs", label: t("res.legend.costs") || "Koszty" },
          { kind: "lost", label: t("res.legend.lost") || "Utracony" },
          { kind: "benefits", label: t("res.legend.benefits") || "Benefity" },
        ].map((item) => (
          <span key={item.kind} className={`legend-item ${item.kind}`}>
            <span className="legend-dot" />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  );
}
