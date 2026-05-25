import { useState, useEffect, useCallback, useRef } from "react";
import { calculateResults } from "../services/api";

const UOP_BENEFITS_MAP = {
  medical: "medical_care",
  sport: "sport_card",
  training: "training_budget",
  ppk: "ppk",
};

const ZUS_MAP = {
  start: "start_relief",
  pref: "preferential",
  full: "full",
};

const TAX_MAP = {
  flat_it: "lump_sum_it",
  linear: "flat_tax",
  scale: "tax_scale",
  ipbox: "ip_box",
};

function mapFormToPayload(s) {
  return {
    calculation_mode: s.mode,
    b2b: {
      monthly_invoice_amount: s.monthlyInvoice,
      monthly_business_costs: s.businessCosts,
      zus_type: ZUS_MAP[s.zusType] || s.zusType,
      sickness_insurance: s.voluntarySick,
      tax_form: TAX_MAP[s.taxForm] || s.taxForm,
      ip_box_qualified_share: s.ipShare,
      ip_box_base_form: s.ipBoxBaseForm,
      vacation_days: s.unpaidVacation,
      sick_days: s.unpaidSick,
      stoppage_months: s.stoppageMonths,
      customBenefits: s.customBenefitsValue,
      age: s.age,
    },
    uop: {
      monthly_gross_salary: s.grossSalary,
      deductible_cost_settings: {
        type: s.kupType === "creative" ? "author_50" : s.kupType,
        creative_work_percentage: s.creativePct,
      },
      youth_relief: s.youthRelief,
      selected_benefits: s.uopBenefits
        .map((b) => UOP_BENEFITS_MAP[b])
        .filter(Boolean),
      age: s.age,
    },
  };
}

function mapResponseToResult(apiRes) {
  if (!apiRes || !apiRes.b2b_results || !apiRes.uop_results) return null;

  const b2bR = apiRes.b2b_results;
  const uopR = apiRes.uop_results;
  const b2bSteps = b2bR.steps || {};
  const uopSteps = uopR.steps || {};

  const b2bZusSocial = b2bSteps.annual_social_contributions || 0;
  const b2bZusHealth = b2bSteps.annual_health_contribution || 0;
  const uopZus = uopR.annual_zus || 0;
  const uopZusHealth = uopSteps.annual_health_contribution ||
    uopSteps.annual_health_insurance || 0;
  const uopZusSocial = uopZusHealth > 0 ? uopZus - uopZusHealth : uopZus;

  const pension = apiRes.pension_limits_2026 || null;

  return {
    b2b: {
      gross: b2bR.annual_revenue || 0,
      net: b2bR.annual_net_income || 0,
      zusSocial: b2bZusSocial,
      zusHealth: b2bZusHealth,
      tax: b2bR.annual_tax || 0,
      costs: b2bR.annual_business_costs || 0,
      lostRevenue: b2bR.annual_lost_revenue || 0,
      customBenefits: (b2bR.annual_custom_benefits_value || 0) + (b2bR.annual_company_benefits_value || 0),
      totalValue: b2bR.total_annual_value || 0,
      monthly: b2bR.monthly_net_income || 0,
      effective: b2bR.annual_revenue > 0 ? (b2bR.annual_tax || 0) / b2bR.annual_revenue : 0,
      solidarity: b2bR.annual_solidarity_tax || 0,
    },
    uop: {
      gross: uopR.annual_gross_salary || 0,
      net: uopR.annual_net_income || 0,
      zusSocial: uopZusSocial,
      zusHealth: uopZusHealth,
      tax: uopR.annual_tax || 0,
      kup: uopSteps.annual_deductible_costs || 0,
      benefits: uopR.annual_benefits_value || 0,
      totalValue: uopR.total_annual_value || 0,
      monthly: uopR.monthly_net_income || 0,
      effective: uopR.annual_gross_salary > 0 ? (uopR.annual_tax || 0) / uopR.annual_gross_salary : 0,
      solidarity: uopR.annual_solidarity_tax || 0,
    },
    diff: (b2bR.total_annual_value || 0) - (uopR.total_annual_value || 0),
    breakeven: apiRes.break_even_invoice_amount || apiRes.break_even_gross_salary || apiRes.break_even_monthly_invoice || 0,
    pension,
    raw: apiRes,
  };
}

function readTheme() {
  try {
    return localStorage.getItem("theme") || "light";
  } catch {
    return "light";
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("theme", theme);
  } catch {
    // ignore
  }
}

export function useCalculatorState() {
  const [mode, setMode] = useState("uop_to_b2b");
  const [age, setAge] = useState(32);
  const [monthlyInvoice, setMonthlyInvoice] = useState(18000);
  const [businessCosts, setBusinessCosts] = useState(800);
  const [zusType, setZusType] = useState("pref");
  const [voluntarySick, setVoluntarySick] = useState(true);
  const [taxForm, setTaxForm] = useState("flat_it");
  const [ipShare, setIpShare] = useState(70);
  const [ipBoxBaseForm, setIpBoxBaseForm] = useState("flat_tax");
  const [grossSalary, setGrossSalary] = useState(14500);
  const [kupType, setKupType] = useState("standard");
  const [creativePct, setCreativePct] = useState(70);
  const [youthRelief, setYouthRelief] = useState(false);
  const [unpaidVacation, setUnpaidVacation] = useState(20);
  const [unpaidSick, setUnpaidSick] = useState(5);
  const [stoppageMonths, setStoppageMonths] = useState(0);
  const [customBenefitsValue, setCustomBenefitsValue] = useState(0);
  const [uopBenefits, setUopBenefits] = useState(["medical", "sport"]);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setThemeState] = useState(readTheme);

  const abortRef = useRef(null);

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setThemeState((t) => (t === "dark" ? "light" : "dark"));
  }, []);

  const formState = {
    mode, age, monthlyInvoice, businessCosts, zusType, voluntarySick,
    taxForm, ipShare, ipBoxBaseForm, grossSalary, kupType, creativePct,
    youthRelief, unpaidVacation, unpaidSick, stoppageMonths,
    customBenefitsValue, uopBenefits,
  };

  useEffect(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const timer = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const payload = mapFormToPayload(formState);
        const apiRes = await calculateResults(payload);
        if (!controller.signal.aborted) {
          setResult(mapResponseToResult(apiRes));
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err?.response?.data?.error || "Błąd obliczenia");
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 250);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    mode, age, monthlyInvoice, businessCosts, zusType, voluntarySick,
    taxForm, ipShare, ipBoxBaseForm, grossSalary, kupType, creativePct,
    youthRelief, unpaidVacation, unpaidSick, stoppageMonths,
    customBenefitsValue, JSON.stringify(uopBenefits),
  ]);

  const handleExportExcel = useCallback(async () => {
    if (!result?.raw) return;
    try {
      const { exportToExcel } = await import("../services/api");
      const { saveAs } = await import("file-saver");
      const blob = await exportToExcel({
        b2b_results: result.raw.b2b_results,
        uop_results: result.raw.uop_results,
      });
      saveAs(blob, "kalkulator_wyniki.xlsx");
    } catch {
      // ignore
    }
  }, [result]);

  const handleShare = useCallback(() => {
    const params = new URLSearchParams();
    params.set("mode", mode);
    params.set("inv", monthlyInvoice);
    params.set("sal", grossSalary);
    params.set("age", age);
    params.set("zus", zusType);
    params.set("tax", taxForm);
    window.history.replaceState({}, "", `${window.location.pathname}?${params}`);
    try {
      navigator.clipboard.writeText(window.location.href);
    } catch {
      // ignore
    }
  }, [mode, monthlyInvoice, grossSalary, age, zusType, taxForm]);

  return {
    // form state + setters
    mode, setMode,
    age, setAge,
    monthlyInvoice, setMonthlyInvoice,
    businessCosts, setBusinessCosts,
    zusType, setZusType,
    voluntarySick, setVoluntarySick,
    taxForm, setTaxForm,
    ipShare, setIpShare,
    ipBoxBaseForm, setIpBoxBaseForm,
    grossSalary, setGrossSalary,
    kupType, setKupType,
    creativePct, setCreativePct,
    youthRelief, setYouthRelief,
    unpaidVacation, setUnpaidVacation,
    unpaidSick, setUnpaidSick,
    stoppageMonths, setStoppageMonths,
    customBenefitsValue, setCustomBenefitsValue,
    uopBenefits, setUopBenefits,
    // result + status
    result, loading, error,
    // actions
    theme, toggleTheme,
    handleExportExcel,
    handleShare,
  };
}
