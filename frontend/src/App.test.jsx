import { render, screen, fireEvent, waitFor } from "./utils/test-utils";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";
import React from "react";
import * as api from "./services/api";

// Mock API calls
vi.mock("./services/api", () => ({
  calculateResults: vi.fn(),
  exportToExcel: vi.fn(),
  calculateBreakEvenAnalysis: vi.fn(),
}));

describe("App", () => {
  beforeEach(() => {
    api.calculateResults.mockReset();
    localStorage.clear();
    document.documentElement.setAttribute("data-theme", "light");
    window.history.replaceState({}, "", "/");

    api.calculateResults.mockResolvedValue({
      b2b_results: {
        total_annual_value: 120000,
        annual_revenue: 150000,
        annual_net_income: 110000,
        annual_zus: 10000,
        annual_tax: 10000,
        monthly_net_income: 10000,
        steps: {},
      },
      uop_results: {
        total_annual_value: 100000,
        annual_gross_salary: 120000,
        annual_net_income: 90000,
        annual_zus: 10000,
        annual_tax: 10000,
        monthly_net_income: 8333,
        steps: {},
      },
      break_even_invoice_amount: 11000,
      config_rates: { uop_employer_overhead: 0.2048, ppk_employer_rate: 0.015 },
    });
  });

  it("renders dark mode toggle and applies data-theme on click", () => {
    render(<App />);
    const toggle = screen.getByTestId("theme-toggle");
    expect(toggle).toBeInTheDocument();

    fireEvent.click(toggle);
    expect(document.documentElement.getAttribute("data-theme")).toBe("dark");
  });

  it("auto-calculates on mount and displays results", async () => {
    render(<App />);

    await waitFor(() => {
      expect(api.calculateResults).toHaveBeenCalled();
      expect(screen.getByTestId("detail-table")).toBeInTheDocument();
    });
  });

  it("updates the URL when share button is clicked", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId("detail-table")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /share|udostępnij/i }));

    expect(window.location.search).toContain("mode=uop_to_b2b");
    expect(window.location.search).toContain("inv=18000");
  });

  it("displays error message if calculateResults fails", async () => {
    api.calculateResults.mockRejectedValue(new Error("API Error"));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Błąd obliczenia")).toBeInTheDocument();
    });
  });

  it("restores state from URL params on mount (valid params)", async () => {
    window.history.replaceState({}, "", "/?inv=20000&mode=b2b_to_uop");
    render(<App />);

    await waitFor(() => {
      expect(api.calculateResults).toHaveBeenCalled();
    });

    const lastCall = api.calculateResults.mock.calls.at(-1)[0];
    expect(lastCall.calculation_mode).toBe("b2b_to_uop");
    expect(lastCall.b2b.monthly_invoice_amount).toBe(20000);
  });

  it("falls back to defaults for garbage URL params", async () => {
    window.history.replaceState({}, "", "/?inv=abc&mode=evil&sal=-999&age=NaN");
    render(<App />);

    await waitFor(() => {
      expect(api.calculateResults).toHaveBeenCalled();
    });

    const lastCall = api.calculateResults.mock.calls.at(-1)[0];
    // Falls back to default mode
    expect(lastCall.calculation_mode).toBe("uop_to_b2b");
    // Falls back to default monthlyInvoice
    expect(lastCall.b2b.monthly_invoice_amount).toBe(18000);
    // Falls back to default grossSalary
    expect(lastCall.uop.monthly_gross_salary).toBe(14500);
  });
});
