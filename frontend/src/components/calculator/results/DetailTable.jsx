import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

function Row({ label, value, minus, total }) {
  return (
    <div className={`detail-row${total ? " total" : ""}`}>
      <span className="k">{label}</span>
      <span className="v">
        {minus && value > 0 ? `−${fmt(value)}` : fmt(value)}
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
          {uop.kup > 0 && <Row label={t("res.detail.kup") || "KUP"} value={uop.kup} minus />}
          {uop.tax > 0 && <Row label={t("res.detail.tax") || "Podatek"} value={uop.tax} minus />}
          <Row label={t("res.detail.net") || "Netto na rękę"} value={uop.net} />
          {uop.benefits > 0 && <Row label={t("res.detail.benefits") || "Benefity UoP"} value={uop.benefits} />}
          <Row label={t("res.detail.total") || "Wartość całkowita"} value={uop.totalValue} total />
        </div>
      </div>
    </div>
  );
}
