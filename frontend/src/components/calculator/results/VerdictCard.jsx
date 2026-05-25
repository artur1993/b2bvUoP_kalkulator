import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

function fmtPct(n) {
  return (n * 100).toFixed(1) + "%";
}

export default function VerdictCard({ result, lang }) {
  const { t } = useTranslation();
  const { diff, b2b, uop } = result;
  const b2bWins = diff > 500;
  const uopWins = diff < -500;
  const winner = b2bWins ? "b2b" : uopWins ? "uop" : "tie";

  const statement =
    b2bWins
      ? t("res.statement_b2b_wins") || "Kontrakt B2B daje więcej"
      : uopWins
      ? t("res.statement_uop_wins") || "Umowa o pracę daje więcej"
      : t("res.statement_tie") || "Wyniki zbliżone";

  const absDiff = Math.abs(diff);

  return (
    <div className="verdict" data-testid="verdict-card">
      <div className="verdict-head">
        <span className="verdict-eyebrow">
          {t("res.eyebrow") || "WERDYKT"}
        </span>
        <span className="verdict-eyebrow" style={{ color: "var(--text-subtle)" }}>
          <span className="live-dot" />
          {t("res.live") || "na żywo"}
        </span>
      </div>

      <div className="verdict-statement">
        {statement}
        {winner !== "tie" && (
          <> · <b>{lang === "pl" ? "o" : "by"}</b></>
        )}
      </div>

      <div className={`verdict-number${winner === "uop" ? " negative" : ""}`}>
        {winner !== "tie" && "+"}{fmt(absDiff)}
        <span style={{ fontSize: 16, color: "var(--text-muted)", marginLeft: 8, fontWeight: 500 }}>
          {t("res.per_year") || "rocznie"}
        </span>
      </div>

      <div className="verdict-meta">
        <div>
          <span className="label">{t("res.per_month") || "miesięcznie"}</span>
          <span className="val">{fmt(absDiff / 12)}</span>
        </div>
        <div>
          <span className="label">{t("res.effective_rate") || "eff. rate"} B2B</span>
          <span className="val">{fmtPct(b2b.effective)}</span>
        </div>
        <div>
          <span className="label">{t("res.effective_rate") || "eff. rate"} UoP</span>
          <span className="val">{fmtPct(uop.effective)}</span>
        </div>
      </div>
    </div>
  );
}
