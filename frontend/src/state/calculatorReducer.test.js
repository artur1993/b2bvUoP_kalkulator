import { describe, expect, it } from "vitest";
import { calculatorReducer, initialState } from "./calculatorReducer";

describe("calculatorReducer", () => {
  it("updates a flat B2B field", () => {
    const state = calculatorReducer(initialState, {
      type: "SET_B2B_FIELD",
      payload: {
        name: "monthly_invoice_amount",
        value: "15000",
        inputType: "number",
        checked: false,
      },
    });

    expect(state.b2bData.monthly_invoice_amount).toBe("15000");
  });

  it("updates nested company benefits", () => {
    const state = calculatorReducer(initialState, {
      type: "SET_B2B_FIELD",
      payload: {
        name: "companyBenefits.paidVacationDays.enabled",
        value: "on",
        inputType: "checkbox",
        checked: true,
      },
    });

    expect(state.b2bData.companyBenefits.paidVacationDays.enabled).toBe(true);
  });

  it("updates UoP selected benefits", () => {
    const state = calculatorReducer(initialState, {
      type: "SET_UOP_FIELD",
      payload: {
        name: "selected_benefits",
        value: "ppk",
        inputType: "checkbox",
        checked: true,
      },
    });

    expect(state.uopData.selected_benefits).toEqual(["ppk"]);
  });

  it("sets age in both data branches and toggles youth relief", () => {
    const state = calculatorReducer(initialState, {
      type: "SET_AGE",
      payload: 24,
    });

    expect(state.b2bData.age).toBe(24);
    expect(state.uopData.age).toBe(24);
    expect(state.uopData.youth_relief).toBe(true);
  });

  it("tracks calculation lifecycle", () => {
    const loadingState = calculatorReducer(initialState, {
      type: "CALCULATE_START",
    });
    const successState = calculatorReducer(loadingState, {
      type: "CALCULATE_SUCCESS",
      payload: { ok: true },
    });

    expect(loadingState.loading).toBe(true);
    expect(successState.loading).toBe(false);
    expect(successState.results).toEqual({ ok: true });
  });
});
