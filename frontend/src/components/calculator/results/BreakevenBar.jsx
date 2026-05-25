import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

export default function BreakevenBar({ result, monthlyInvoice, grossSalary, mode }) {
  const { t, i18n } = useTranslation();
  const { breakeven } = result;

  if (!breakeven || breakeven <= 0) return null;

  const curRate = mode === "uop_to_b2b" ? monthlyInvoice : grossSalary;
  const minR = Math.min(curRate, breakeven) * 0.6;
  const maxR = Math.max(curRate, breakeven) * 1.4;
  const range = maxR - minR || 1;
  const scale = (v) => Math.min(98, Math.max(2, ((v - minR) / range) * 100));

  const bePos = scale(breakeven);
  const curPos = scale(curRate);
  const beAbove = curRate >= breakeven;
  const gap = Math.abs(curRate - breakeven);

  return (
    <div className="breakeven" data-testid="breakeven-bar">
      <div className="breakeven-head">
        <h4>{t("res.breakeven_title") || "Próg opłacalności"}</h4>
        <span className="hint">{t("res.breakeven_sub")}</span>
      </div>

      <div className="be-bar">
        {/* Parity marker */}
        <span className="be-marker" style={{ left: `${bePos}%` }} />
        <span className="be-label parity" style={{ left: `${bePos}%` }}>
          {t("res.breakeven_eq") || "Parity"}: {fmt(breakeven)}
        </span>

        {/* Current rate marker */}
        <span className="be-current" style={{ left: `${curPos}%` }} />
        <span className="be-label current" style={{ left: `${curPos}%` }}>
          {t("res.breakeven_now") || "Aktualna"}: {fmt(curRate)}
        </span>
      </div>

      <div className="be-footer">
        <div>
          <span className="label">{t("res.breakeven_eq") || "Próg parity"}</span>
          <span className="val">
            {fmt(breakeven)}{" "}
            <span style={{ color: "var(--text-subtle)", fontSize: 11, fontWeight: 400 }}>
              / {i18n.language?.startsWith("pl") ? "mies." : "mo"}
            </span>
          </span>
        </div>
        <div>
          <span className="label">
            {beAbove
              ? t("res.breakeven_gap") || "Powyżej progu o"
              : t("res.breakeven_below") || "Poniżej progu o"}
          </span>
          <span className="val" style={{ color: beAbove ? "var(--positive)" : "var(--negative)" }}>
            {fmt(gap)}
          </span>
        </div>
      </div>
    </div>
  );
}
