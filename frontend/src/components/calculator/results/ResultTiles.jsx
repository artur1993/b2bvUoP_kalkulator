import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 }).format(n);
}

export default function ResultTiles({ result, lang }) {
  const { t } = useTranslation();
  const { diff, b2b, uop } = result;
  const winner = diff > 500 ? "b2b" : diff < -500 ? "uop" : "tie";

  return (
    <div className="tiles" data-testid="result-tiles">
      <div className={`tile${winner === "b2b" ? " winner" : ""}`}>
        <div className="tile-head">
          <span className="name">
            <span className="badge b2b">B2B</span>
            {t("res.take_home") || "Wartość roczna"}
          </span>
          {winner === "b2b" && (
            <span className="crown">★ {lang === "pl" ? "lider" : "leads"}</span>
          )}
        </div>
        <div className="big">{fmt(b2b.totalValue)}</div>
        <div className="sub">
          {t("res.monthly_avg") || "Średnio mies."}: {fmt(b2b.monthly)}
        </div>
      </div>

      <div className={`tile${winner === "uop" ? " winner" : ""}`}>
        <div className="tile-head">
          <span className="name">
            <span className="badge uop">UoP</span>
            {t("res.take_home") || "Wartość roczna"}
          </span>
          {winner === "uop" && (
            <span className="crown">★ {lang === "pl" ? "lider" : "leads"}</span>
          )}
        </div>
        <div className="big">{fmt(uop.totalValue)}</div>
        <div className="sub">
          {t("res.monthly_avg") || "Średnio mies."}: {fmt(uop.monthly)}
        </div>
      </div>
    </div>
  );
}
