import React from "react";
import { render, screen } from "../../../utils/test-utils";
import { describe, it, expect } from "vitest";
import "@testing-library/jest-dom";
import DetailTable from "./DetailTable";
import i18n from "../../../i18n";

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
    ppkBreakdown: { employee: 2400, employer: 1800, state: 240 },
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
    render(<DetailTable result={withPpk(4440)} />);
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
});
