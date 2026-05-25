import React from "react";
import { useTranslation } from "react-i18next";

function fmt(n) {
  return new Intl.NumberFormat("pl-PL", { maximumFractionDigits: 0 }).format(n);
}

export default function PensionNote({ pension }) {
  const { t } = useTranslation();
  if (!pension) return null;

  return (
    <div className="pension-note" data-testid="pension-note">
      <div className="pension-icon">i</div>
      <div className="body">
        <strong>{t("results.pension_info_title") || "Pamiętaj o emeryturze"}</strong>
        <span>
          {t("results.pension_info_prefix") || "Rozważ"}{" "}
          <b>{t("results.pension_info_ike") || "IKE"}</b>{" "}
          {t("results.pension_info_or") || "lub"}{" "}
          <b>{t("results.pension_info_ikze") || "IKZE"}</b>.{" "}
          {t("results.pension_info_limits", {
            ike: fmt(pension.ike),
            ikzeStandard: fmt(pension.ikze_standard),
            ikzeB2b: fmt(pension.ikze_b2b),
          })}
        </span>
      </div>
    </div>
  );
}
