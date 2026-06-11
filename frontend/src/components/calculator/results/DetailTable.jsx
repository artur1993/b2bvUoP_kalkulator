import React from "react";
import { useTranslation } from "react-i18next";
import Tooltip from "./Tooltip";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

function KupTooltipContent({ kb, t }) {
  if (!kb) return null;
  const typeLabels = {
    author_50: t("res.detail.kup_tooltip.type_author"),
    standard: t("res.detail.kup_tooltip.type_standard"),
    elevated: t("res.detail.kup_tooltip.type_elevated"),
    none: t("res.detail.kup_tooltip.type_none"),
  };
  return (
    <div>
      <strong>{t("res.detail.kup_tooltip.title")}</strong>
      <div style={{ marginTop: 4 }}>{t("res.detail.kup_tooltip.type")}: {typeLabels[kb.type] || kb.type}</div>
      {kb.type === "author_50" && (
        <div>{t("res.detail.kup_tooltip.creative_pct")}: {kb.creative_work_percentage}%</div>
      )}
      <div>{t("res.detail.kup_tooltip.annual")}: {fmt(kb.annual_amount)}</div>
      {kb.type === "author_50" && (
        <div>
          {t("res.detail.kup_tooltip.limit")}: {fmt(kb.limit)}
          {kb.limit_reached ? ` ⚠ ${t("res.detail.kup_tooltip.limit_reached")}` : " ✓"}
        </div>
      )}
    </div>
  );
}

function TaxTooltipContent({ tb, t }) {
  if (!tb) return null;
  const rateFirst = Math.round((tb.rate_first_bracket ?? 0.12) * 100);
  const rateSecond = Math.round((tb.rate_second_bracket ?? 0.32) * 100);
  return (
    <div>
      <strong>{t("res.detail.tax_tooltip.title")}</strong>
      <div style={{ marginTop: 4 }}>{t("res.detail.tax_tooltip.taxable_base")}: {fmt(tb.annual_taxable_base)}</div>
      <div style={{ marginTop: 4 }}>
        {t("res.detail.tax_tooltip.first_bracket")} ({fmt(tb.base_first_bracket)} × {rateFirst}%): {fmt(tb.tax_first_bracket)}
      </div>
      {tb.base_second_bracket > 0 && (
        <div>
          {t("res.detail.tax_tooltip.second_bracket")} ({fmt(tb.base_second_bracket)} × {rateSecond}%): {fmt(tb.tax_second_bracket)}
        </div>
      )}
      <div>
        {t("res.detail.tax_tooltip.tax_free")} ({fmt(tb.tax_free_amount)} × {rateFirst}%): −{fmt(tb.tax_reducing_applied)}
      </div>
      <div style={{ borderTop: "1px solid var(--border-muted)", marginTop: 4, paddingTop: 4 }}>
        <strong>{t("res.detail.tax_tooltip.total")}: {fmt(tb.annual_net_tax)}</strong>
      </div>
    </div>
  );
}

function PpkTooltipContent({ pb, t }) {
  if (!pb) return null;
  return (
    <div>
      <strong>{t("res.detail.ppk_tooltip.title")}</strong>
      <div style={{ marginTop: 4 }}>{t("res.detail.ppk_tooltip.note")}</div>
      <div style={{ marginTop: 4 }}>{t("res.detail.ppk_tooltip.employee")}: {fmt(pb.employee)}</div>
      <div>{t("res.detail.ppk_tooltip.employer")}: {fmt(pb.employer)}</div>
      {pb.state > 0 && <div>{t("res.detail.ppk_tooltip.state")}: {fmt(pb.state)}</div>}
    </div>
  );
}

function Row({ label, value, minus, plus, total, accent, tooltip }) {
  const labelEl = tooltip
    ? <Tooltip text={tooltip} width={300}>{label}</Tooltip>
    : label;
  return (
    <div className={`detail-row${total ? " total" : ""}${accent ? " accent" : ""}`}>
      <span className="k">{labelEl}</span>
      <span className="v">
        {plus ? `+${fmt(value)}` : minus && value > 0 ? `−${fmt(value)}` : fmt(value)}
      </span>
    </div>
  );
}

export default function DetailTable({ result }) {
  const { t } = useTranslation();
  const { b2b, uop } = result;

  return (
    <div className="detail" data-testid="detail-table">
      <div className="detail-head">
        <h4>{t("res.detail_title") || "Roczne rozliczenie"}</h4>
      </div>
      <div className="detail-grid">
        <div className="detail-col">
          <h5>
            <span className="badge b2b">B2B</span>
          </h5>
          <Row label={t("res.detail.gross_b2b") || "Przychód roczny"} value={b2b.gross} />
          {b2b.costs > 0 && <Row label={t("res.detail.business_costs") || "Koszty firmowe"} value={b2b.costs} minus />}
          {(b2b.zusSocial + b2b.zusHealth) > 0 && (
            <Row label={t("res.detail.zus_social") || "ZUS"} value={b2b.zusSocial + b2b.zusHealth} minus />
          )}
          {b2b.tax > 0 && <Row label={t("res.detail.tax") || "Podatek"} value={b2b.tax} minus />}
          {b2b.lostRevenue > 0 && <Row label={t("res.detail.lost_revenue") || "Utracony przychód"} value={b2b.lostRevenue} minus />}
          <Row label={t("res.detail.net") || "Netto na rękę"} value={b2b.net} />
          {b2b.customBenefits > 0 && <Row label={t("res.detail.custom_benefits") || "Benefity B2B"} value={b2b.customBenefits} />}
          <Row label={t("res.detail.total") || "Wartość całkowita"} value={b2b.totalValue} total />
        </div>

        <div className="detail-col">
          <h5>
            <span className="badge uop">UoP</span>
          </h5>
          <Row label={t("res.detail.gross_uop") || "Wynagrodzenie brutto"} value={uop.gross} />
          {(uop.zusSocial + uop.zusHealth) > 0 && (
            <Row label={t("res.detail.zus_social") || "ZUS"} value={uop.zusSocial + uop.zusHealth} minus />
          )}
          {uop.kup > 0 && (
            <Row
              label={t("res.detail.kup") || "KUP"}
              value={uop.kup}
              minus
              tooltip={uop.kupBreakdown ? <KupTooltipContent kb={uop.kupBreakdown} t={t} /> : null}
            />
          )}
          {uop.tax > 0 && (
            <Row
              label={t("res.detail.tax") || "Podatek"}
              value={uop.tax}
              minus
              tooltip={uop.taxBreakdown ? <TaxTooltipContent tb={uop.taxBreakdown} t={t} /> : null}
            />
          )}
          <Row label={t("res.detail.net") || "Netto na rękę"} value={uop.net} />
          {uop.customBenefits > 0 && <Row label={t("res.detail.uop_custom_benefits") || "Własne benefity UoP"} value={uop.customBenefits} />}
          {uop.benefits > 0 && <Row label={t("res.detail.benefits") || "Benefity UoP"} value={uop.benefits} />}
          {uop.ppkCapital > 0 && (
            <Row
              label={t("res.detail.ppk_capital") || "Oszczędności PPK (Twój kapitał)"}
              value={uop.ppkCapital}
              plus
              accent
              tooltip={<PpkTooltipContent pb={uop.ppkBreakdown} t={t} />}
            />
          )}
          <Row label={t("res.detail.total") || "Wartość całkowita"} value={uop.totalValue} total />
        </div>
      </div>
    </div>
  );
}
