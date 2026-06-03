import React from "react";
import { useTranslation } from "react-i18next";
import { useCalculatorState } from "./state/useCalculatorState";
import FormCluster, { SubsecTitle } from "./components/calculator/FormCluster";
import Field from "./components/calculator/Field";
import NumberInput from "./components/calculator/controls/NumberInput";
import PillList from "./components/calculator/controls/PillList";
import Toggle from "./components/calculator/controls/Toggle";
import Slider from "./components/calculator/controls/Slider";
import CheckList from "./components/calculator/controls/CheckList";
import VerdictCard from "./components/calculator/results/VerdictCard";
import ResultTiles from "./components/calculator/results/ResultTiles";
import CompositionBars from "./components/calculator/results/CompositionBars";
import BreakevenBar from "./components/calculator/results/BreakevenBar";
import DetailTable from "./components/calculator/results/DetailTable";
import PensionNote from "./components/calculator/results/PensionNote";

function SunIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
      <path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98" />
    </svg>
  );
}

export default function App() {
  const { i18n } = useTranslation();
  const { t } = useTranslation();
  const s = useCalculatorState();

  const zusOptions = [
    { value: "start", label: t("form.zus_start_relief") },
    { value: "pref", label: t("form.zus_preferential") },
    { value: "full", label: t("form.zus_full") },
  ];

  const taxOptions = [
    { value: "flat_it", label: t("form.tax_flat_it") },
    { value: "linear", label: t("form.tax_linear") },
    { value: "scale", label: t("form.tax_scale") },
    { value: "ipbox", label: t("form.tax_ip_box") },
  ];

  const ipBoxBaseOptions = [
    { value: "flat_tax", label: t("form.ip_box_base_flat_tax") },
    { value: "tax_scale", label: t("form.ip_box_base_tax_scale") },
  ];

  const kupOptions = [
    { value: "standard", label: t("form.kup_standard") },
    { value: "elevated", label: t("form.kup_elevated") },
    { value: "creative", label: t("form.kup_creative_50") },
    { value: "none", label: t("form.kup_none") },
  ];

  const uopBenefitOptions = [
    { value: "medical", label: t("form.benefit_medical") },
    { value: "sport", label: t("form.benefit_sport") },
    { value: "training", label: t("form.benefit_training") },
    { value: "ppk", label: t("form.benefit_ppk") },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      {/* Topbar */}
      <header className="topbar">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 7,
            background: "var(--text)", color: "var(--bg)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'JetBrains Mono', monospace", fontSize: 12, fontWeight: 700,
            flexShrink: 0,
          }}>
            B²
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, lineHeight: 1.2 }}>
              {t("header.title", { year: "2026" })}
            </div>
            <div style={{ fontSize: 11.5, color: "var(--text-subtle)", lineHeight: 1.2 }}>
              {t("header.subtitle")}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div className="lang-toggle">
            <button
              className={i18n.language?.startsWith("pl") ? "active" : ""}
              onClick={() => i18n.changeLanguage("pl")}
            >
              PL
            </button>
            <button
              className={i18n.language?.startsWith("en") ? "active" : ""}
              onClick={() => i18n.changeLanguage("en")}
            >
              EN
            </button>
          </div>
          <button
            className="icon-btn"
            data-testid="theme-toggle"
            aria-pressed={s.theme === "dark"}
            onClick={s.toggleTheme}
          >
            {s.theme === "dark" ? <SunIcon /> : <MoonIcon />}
          </button>
        </div>
      </header>

      {/* Main layout */}
      <div className="layout">
        {/* LEFT: Form */}
        <div className="col-form">
          {/* Mode strip */}
          <div className="mode-strip">
            <button
              className={s.mode === "uop_to_b2b" ? "active" : ""}
              onClick={() => s.setMode("uop_to_b2b")}
              data-testid="uop-to-b2b-radio"
            >
              {t("form.uop_to_b2b_mode")}
            </button>
            <button
              className={s.mode === "b2b_to_uop" ? "active" : ""}
              onClick={() => s.setMode("b2b_to_uop")}
              data-testid="b2b-to-uop-radio"
            >
              {t("form.b2b_to_uop_mode")}
            </button>
          </div>

          {/* Profile */}
          <FormCluster title={t("sec.profile") || "Profil"}>
            <Field
              label={t("form.age")}
              help={t("field_help.age")}
              control={
                <NumberInput
                  value={s.age}
                  onChange={s.setAge}
                  min={16}
                  max={100}
                  suffix={i18n.language === "pl" ? "lat" : "yr"}
                />
              }
            />
          </FormCluster>

          {/* B2B */}
          <FormCluster badge="B2B" badgeClass="b2b" title={t("sec.b2b") || t("form.b2b_title")} sub={t("sec.b2b_sub")}>
            <SubsecTitle>{i18n.language === "pl" ? "Finanse" : "Financials"}</SubsecTitle>
            <Field
              label={t("form.monthly_invoice")}
              help={t("field_help.monthly_invoice")}
              control={<NumberInput value={s.monthlyInvoice} onChange={s.setMonthlyInvoice} suffix="zł" step={500} />}
            />
            <Field
              label={t("form.business_costs")}
              help={t("field_help.business_costs")}
              control={<NumberInput value={s.businessCosts} onChange={s.setBusinessCosts} suffix="zł" step={100} />}
            />

            <SubsecTitle>ZUS</SubsecTitle>
            <Field
              label={t("form.zus_type")}
              control={<PillList value={s.zusType} onChange={s.setZusType} options={zusOptions} />}
            />
            <Field
              label={t("form.voluntary_sick_leave")}
              help={t("field_help.voluntary_sick")}
              control={<Toggle value={s.voluntarySick} onChange={s.setVoluntarySick} />}
            />

            <SubsecTitle>{i18n.language === "pl" ? "Opodatkowanie" : "Taxation"}</SubsecTitle>
            <Field
              label={t("form.tax_form")}
              control={<PillList value={s.taxForm} onChange={s.setTaxForm} options={taxOptions} />}
            />

            {s.taxForm === "ipbox" && (
              <>
                <Field
                  label={t("form.ip_box_qualified_share")}
                  help={t("field_help.ip_share")}
                  control={<Slider value={s.ipShare} onChange={s.setIpShare} min={0} max={100} step={5} suffix="%" />}
                />
                <Field
                  label={t("form.ip_box_base_form")}
                  control={
                    <select
                      className="field-select"
                      value={s.ipBoxBaseForm}
                      onChange={(e) => s.setIpBoxBaseForm(e.target.value)}
                    >
                      {ipBoxBaseOptions.map((o) => (
                        <option key={o.value} value={o.value}>{o.label}</option>
                      ))}
                    </select>
                  }
                />
                <div className="ip-warning">{t("form.ip_box_warning")}</div>
              </>
            )}
          </FormCluster>

          {/* UoP */}
          <FormCluster badge="UoP" badgeClass="uop" title={t("sec.uop") || t("form.uop_title")} sub={t("sec.uop_sub")}>
            <SubsecTitle>{i18n.language === "pl" ? "Finanse" : "Financials"}</SubsecTitle>
            <Field
              label={t("form.gross_salary")}
              help={t("field_help.gross_salary")}
              control={<NumberInput value={s.grossSalary} onChange={s.setGrossSalary} suffix="zł" step={500} />}
            />
            <Field
              label={t("form.kup_type")}
              control={<PillList value={s.kupType} onChange={s.setKupType} options={kupOptions} />}
            />
            {s.kupType === "creative" && (
              <Field
                label={t("form.creative_work_percentage")}
                help={i18n.language === "pl" ? "Limit roczny KUP autorskich: 120 000 zł" : "Annual KUP cap: 120,000 PLN"}
                control={<Slider value={s.creativePct} onChange={s.setCreativePct} min={0} max={100} step={5} suffix="%" />}
              />
            )}
            <Field
              label={t("form.youth_relief")}
              help={t("field_help.youth_relief")}
              control={<Toggle value={s.youthRelief} onChange={s.setYouthRelief} data-testid="youth-relief-uop" />}
            />
            <Field
              label={t("form.annual_bonus")}
              help={t("field_help.annual_bonus")}
              control={<Slider value={s.uopBonusPct} onChange={s.setUopBonusPct} min={0} max={100} step={5} suffix="%" />}
            />

            <SubsecTitle>{t("form.benefits")}</SubsecTitle>
            <Field
              full
              control={
                <CheckList
                  value={s.uopBenefits}
                  onChange={s.setUopBenefits}
                  options={uopBenefitOptions}
                />
              }
            />
            <Field
              label={t("form.uop_custom_benefits")}
              help={t("field_help.uop_custom_benefits")}
              control={<NumberInput value={s.uopCustomBenefitsValue} onChange={s.setUopCustomBenefitsValue} suffix="zł" step={500} />}
            />
          </FormCluster>

          {/* Time off */}
          <FormCluster title={t("sec.timeoff") || t("form.time_off_stoppage")} sub={t("sec.timeoff_sub")}>
            <Field
              label={t("form.holidays_paid")}
              help={t("field_help.holidays_paid")}
              control={<Toggle value={s.holidaysPaid} onChange={s.setHolidaysPaid} />}
            />
            <Field
              label={t("form.unpaid_vacation")}
              control={<Slider value={s.totalVacation} onChange={s.setTotalVacation} min={0} max={40} step={1} suffix="d" />}
            />
            <Field
              label={t("form.paid_vacation")}
              help={t("field_help.paid_vacation")}
              control={<Slider value={s.paidVacation} onChange={s.setPaidVacation} min={0} max={40} step={1} suffix="d" />}
            />
            <Field
              label={t("form.unpaid_sick")}
              control={<Slider value={s.unpaidSick} onChange={s.setUnpaidSick} min={0} max={30} step={1} suffix="d" />}
            />
            <Field
              label={t("form.stoppage_months")}
              help={t("field_help.stoppage_months")}
              control={<Slider value={s.stoppageMonths} onChange={s.setStoppageMonths} min={0} max={6} step={1} suffix="m" />}
            />
          </FormCluster>

          {/* Custom benefits */}
          <FormCluster title={t("sec.benefits_custom") || t("form.benefits")}>
            <Field
              label={t("form.custom_benefits_value")}
              control={<NumberInput value={s.customBenefitsValue} onChange={s.setCustomBenefitsValue} suffix="zł" step={500} />}
            />
          </FormCluster>
        </div>

        {/* RIGHT: Results */}
        <div className="col-results" data-testid="results-display">
          {s.loading && !s.result && (
            <div className="results-loading">
              <div className="spinner" />
            </div>
          )}

          {!s.loading && !s.result && !s.error && (
            <div className="results-empty">
              <div className="icon">⟳</div>
              <div style={{ fontSize: 13 }}>
                {i18n.language === "pl" ? "Wypełnij formularz aby zobaczyć wyniki" : "Fill in the form to see results"}
              </div>
            </div>
          )}

          {s.error && (
            <div style={{
              padding: "14px 16px",
              background: "oklch(96% 0.03 25)",
              border: "1px solid oklch(88% 0.06 25)",
              borderRadius: "var(--radius)",
              fontSize: 13,
              color: "var(--negative)",
            }}>
              {s.error}
            </div>
          )}

          {s.result && (
            <>
              <VerdictCard result={s.result} lang={i18n.language} />
              <ResultTiles result={s.result} lang={i18n.language} />
              <CompositionBars result={s.result} />
              <BreakevenBar result={s.result} monthlyInvoice={s.monthlyInvoice} grossSalary={s.grossSalary} mode={s.mode} />
              <DetailTable result={s.result} />
              {s.result.pension && <PensionNote pension={s.result.pension} />}
              <div className="footer-actions">
                <button className="btn primary" data-testid="export-excel-button" onClick={s.handleExportExcel}>
                  <DownloadIcon />
                  {t("results.export_excel")}
                </button>
                <button className="btn" onClick={s.handleShare}>
                  <ShareIcon />
                  {t("res.export_share") || (i18n.language === "pl" ? "Udostępnij" : "Share")}
                </button>
              </div>
              <div className="footnote">
                {t("res.footnote") || (i18n.language === "pl"
                  ? "Obliczenia według przepisów 2026. Nie stanowią porady podatkowej."
                  : "Calculations based on 2026 regulations. Not tax advice.")}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
