import React from "react";
import { render, screen, fireEvent } from "../../../utils/test-utils";
import { describe, it, expect } from "vitest";
import "@testing-library/jest-dom";
import DetailTable from "./DetailTable";
import i18n from "../../../i18n";

// employer netto (po PIT) — nie brutto
const EMPLOYEE = 2400;
const EMPLOYER_NET = 1584;
const STATE = 240;
const PPK_CAPITAL = EMPLOYEE + EMPLOYER_NET + STATE; // 4224

const baseResult = {
  b2b: {
    gross: 200000,
    costs: 0,
    zusSocial: 0,
    zusHealth: 0,
    tax: 24000,
    lostRevenue: 0,
    net: 150000,
    customBenefits: 0,
    totalValue: 150000,
  },
  uop: {
    gross: 120000,
    zusSocial: 16000,
    zusHealth: 9000,
    tax: 8000,
    kup: 3000,
    kupBreakdown: null,
    taxBreakdown: null,
    net: 84000,
    customBenefits: 0,
    benefits: 0,
    ppkCapital: 0,
    ppkBreakdown: { employee: EMPLOYEE, employer: EMPLOYER_NET, state: STATE },
    totalValue: 84000,
  },
};

function withPpk(ppkCapital) {
  return {
    ...baseResult,
    uop: { ...baseResult.uop, ppkCapital, totalValue: baseResult.uop.net + ppkCapital },
  };
}

describe("DetailTable — linia kapitału PPK", () => {
  it("pokazuje wyróżnioną linię kapitału PPK z prefiksem '+', gdy ppkCapital > 0", () => {
    render(<DetailTable result={withPpk(PPK_CAPITAL)} />);
    const label = i18n.t("res.detail.ppk_capital");
    const labelEl = screen.getByText(label);
    expect(labelEl).toBeInTheDocument();
    const row = labelEl.closest(".detail-row");
    expect(row).toHaveClass("accent");
    expect(row.textContent).toContain("+");
  });

  it("ukrywa linię kapitału PPK, gdy ppkCapital = 0", () => {
    render(<DetailTable result={withPpk(0)} />);
    const label = i18n.t("res.detail.ppk_capital");
    expect(screen.queryByText(label)).not.toBeInTheDocument();
  });

  it("tooltip PPK pokazuje rozbicie: pracownik, pracodawca (netto po PIT), dopłata państwa", () => {
    render(<DetailTable result={withPpk(PPK_CAPITAL)} />);

    // kliknij przycisk ? przy PPK aby otworzyć tooltip
    const label = i18n.t("res.detail.ppk_capital");
    const labelEl = screen.getByText(label);
    const infoBtn = labelEl.closest(".detail-row").querySelector('button[aria-label="info"]');
    expect(infoBtn).not.toBeNull();
    fireEvent.click(infoBtn);

    // tooltip content sprawdza employer NETTO
    const employerLabel = i18n.t("res.detail.ppk_tooltip.employer");
    expect(screen.getByText(new RegExp(employerLabel.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")))).toBeInTheDocument();

    // wartość netto pracodawcy musi być widoczna w tooltipie
    expect(screen.getByText(/1\s*584|1584/)).toBeInTheDocument();
  });

  it("suma rozbicia PPK (pracownik + pracodawca netto + państwo) równa się ppkCapital", () => {
    const result = withPpk(PPK_CAPITAL);
    const { employee, employer, state } = result.uop.ppkBreakdown;
    expect(employee + employer + state).toBe(PPK_CAPITAL);
  });
});
