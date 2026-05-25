import { render, screen, fireEvent, waitFor } from "../utils/test-utils";
import { describe, it, expect, vi, beforeEach } from "vitest";
import CalculatorForm from "./CalculatorForm";
import React, { useReducer } from "react";
import i18n from "../i18n";
import { calculatorReducer, initialState } from "../state/calculatorReducer";

describe("CalculatorForm", () => {
  const mockOnCalculate = vi.fn();
  const mockOnExport = vi.fn();

  const initialB2bData = {
    monthly_invoice_amount: 0,
    monthly_business_costs: 0,
    zus_type: "preferential",
    sickness_insurance: false,
    tax_form: "flat_tax",
    vacation_days: 0,
    sick_days: 0,
    stoppage_months: 0,
    customBenefits: 0,
    ip_box_qualified_share: 100,
    ip_box_base_form: "flat_tax",
    companyBenefits: {
      paidVacationDays: { enabled: false, days: 0, value: 0 },
      paidSickDays: { enabled: false, days: 0, value: 0 },
      medicalCare: { enabled: false, value: 0 },
      lifeInsurance: { enabled: false, value: 0 },
      sportCard: { enabled: false, value: 0 },
      trainingBudget: { enabled: false, value: 0 },
      otherBenefits: { enabled: false, value: 0 },
    },
  };

  const initialUopData = {
    monthly_gross_salary: 0,
    deductible_cost_settings: {
      type: "standard",
      creative_work_percentage: 70,
    },
    youth_relief: false,
    selected_benefits: [],
  };

  // Test Wrapper component to manage state
  const TestWrapper = ({
    initialB2b,
    initialUop,
    onCalculate,
    loading,
    initialCalculationMode,
  }) => {
    const [state, dispatch] = useReducer(calculatorReducer, {
      ...initialState,
      b2bData: initialB2b,
      uopData: initialUop,
      loading,
      calculationMode: initialCalculationMode || "uop_to_b2b",
    });

    return (
      <CalculatorForm
        state={state}
        dispatch={dispatch}
        handleCalculate={onCalculate}
      />
    );
  };

  beforeEach(() => {
    mockOnCalculate.mockClear();
    mockOnExport.mockClear();
  });

  const renderComponent = (b2b = initialB2bData, uop = initialUopData) => {
    render(
      <TestWrapper
        initialB2b={b2b}
        initialUop={uop}
        onCalculate={mockOnCalculate}
        loading={false}
      />,
    );
  };

  it("renders all form fields correctly", () => {
    renderComponent();

    // Check for B2B fields
    expect(screen.getByLabelText("Monthly Invoice (PLN)")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Monthly Business Costs (PLN)"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("ZUS Type")).toBeInTheDocument();
    expect(screen.getByLabelText("Taxation Form")).toBeInTheDocument();
    expect(screen.queryByTestId("youth-relief-b2b")).not.toBeInTheDocument();
    expect(
      screen.getByLabelText("Annual Vacation Days (unpaid)"),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText("Annual Sick Days (unpaid)"),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText("Months of Stoppage/No Projects"),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText("Custom Annual Benefits Value (PLN)"),
    ).toBeInTheDocument();

    // Check for UoP fields
    expect(
      screen.getByLabelText("Gross Monthly Salary (PLN)"),
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText("Type of Tax-Deductible Costs"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("youth-relief-uop")).toBeInTheDocument();
    expect(screen.getByLabelText("Medical Care")).toBeInTheDocument();
    expect(screen.getByLabelText("Sport Card")).toBeInTheDocument();

    // Check for buttons
    expect(
      screen.getByRole("button", { name: "Calculate Comparison" }),
    ).toBeInTheDocument();
  });

  it("renders supported ZUS options including start relief", () => {
    renderComponent();

    const zusSelect = screen.getByLabelText("ZUS Type");
    const optionValues = [...zusSelect.options].map((option) => option.value);

    expect(optionValues).toEqual(["start_relief", "preferential", "full"]);
    expect(optionValues).not.toContain("small_business");
  });

  it("updates B2B input fields correctly", async () => {
    renderComponent();
    const fakturaInput = screen.getByLabelText("Monthly Invoice (PLN)");
    fireEvent.change(fakturaInput, {
      target: { name: "monthly_invoice_amount", value: "15000" },
    });
    await waitFor(() => {
      expect(fakturaInput).toHaveValue(15000);
    });

    const costsInput = screen.getByLabelText("Monthly Business Costs (PLN)");
    fireEvent.change(costsInput, {
      target: { name: "monthly_business_costs", value: "500" },
    });
    await waitFor(() => {
      expect(costsInput).toHaveValue(500);
    });
  });

  it("shows IP Box fields only when IP Box is selected", async () => {
    renderComponent();

    expect(
      screen.queryByLabelText("Qualified IP Income Share (%)"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByLabelText("Tax Form for Non-Qualified Income"),
    ).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Taxation Form"), {
      target: { name: "tax_form", value: "ip_box" },
    });

    await waitFor(() => {
      expect(
        screen.getByLabelText("Qualified IP Income Share (%)"),
      ).toBeInTheDocument();
    });
    expect(
      screen.getByLabelText("Tax Form for Non-Qualified Income"),
    ).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("nexus");
  });

  it("updates UoP input fields correctly", async () => {
    renderComponent();
    const wynagrodzenieInput = screen.getByLabelText(
      "Gross Monthly Salary (PLN)",
    );
    fireEvent.change(wynagrodzenieInput, {
      target: { name: "monthly_gross_salary", value: "8000" },
    });
    await waitFor(() => {
      expect(wynagrodzenieInput).toHaveValue(8000);
    });
  });

  it("calls onCalculate on form submission", () => {
    renderComponent();
    fireEvent.click(
      screen.getByRole("button", { name: "Calculate Comparison" }),
    );
    expect(mockOnCalculate).toHaveBeenCalledTimes(1);
  });

  // New tests for company benefits
  const companyBenefits = [
    {
      label: "Paid Vacation Days (from company)",
      id: "paidVacationDays",
      type: "days",
      testId: "paid-vacation",
    },
    {
      label: "Paid Sick Days (from company)",
      id: "paidSickDays",
      type: "days",
      testId: "paid-sick",
    },
    {
      label: "Medical Care (from company)",
      id: "medicalCare",
      type: "value",
      testId: "medical-care",
    },
    {
      label: "Life Insurance (from company)",
      id: "lifeInsurance",
      type: "value",
      testId: "life-insurance",
    },
    {
      label: "Sport Card (from company)",
      id: "sportCard",
      type: "value",
      testId: "sport-card",
    },
    {
      label: "Training Budget (from company)",
      id: "trainingBudget",
      type: "value",
      testId: "training-budget",
    },
    {
      label: "Other Benefits (from company)",
      id: "otherBenefits",
      type: "value",
      testId: "other-benefits",
    },
  ];

  companyBenefits.forEach((benefit) => {
    it(`toggles ${benefit.label} and updates its value correctly`, async () => {
      renderComponent();
      const checkbox = screen.getByTestId(`${benefit.testId}-checkbox`);

      // Enable the benefit
      fireEvent.click(checkbox);
      await waitFor(() => {
        expect(checkbox).toBeChecked();
      });

      // Check if the input field appears and update its value
      const input = screen.getByTestId(`${benefit.testId}-input`);
      let inputValue = "";
      if (benefit.type === "days") {
        inputValue = "10";
      } else {
        inputValue = "1000";
      }

      fireEvent.change(input, {
        target: {
          name: `companyBenefits.${benefit.id}.${benefit.type === "days" ? "days" : "value"}`,
          value: inputValue,
        },
      });
      await waitFor(() => {
        expect(input).toHaveValue(parseInt(inputValue));
      });

      // Disable the benefit
      fireEvent.click(checkbox);
      await waitFor(() => {
        expect(checkbox).not.toBeChecked();
      });
      // Ensure the input field is no longer in the document
      expect(
        screen.queryByTestId(`${benefit.testId}-input`),
      ).not.toBeInTheDocument();
    });
  });

  it("updates UoP selected benefits correctly", async () => {
    renderComponent();
    const medicalCareCheckbox = screen.getByLabelText("Medical Care");
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).toBeChecked();
    });

    const sportCardCheckbox = screen.getByLabelText("Sport Card");
    fireEvent.click(sportCardCheckbox);
    await waitFor(() => {
      expect(sportCardCheckbox).toBeChecked();
    });

    // Uncheck one
    fireEvent.click(medicalCareCheckbox);
    await waitFor(() => {
      expect(medicalCareCheckbox).not.toBeChecked();
    });
    expect(sportCardCheckbox).toBeChecked(); // Other should remain checked
  });

  it("renders only active UoP benefit options while keeping company life cover", () => {
    renderComponent();

    expect(
      screen.getAllByRole("checkbox", { name: "Medical Care" }),
    ).toHaveLength(1);
    expect(
      screen.getByRole("checkbox", { name: "Sport Card" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: "Training" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "PPK" })).toBeInTheDocument();
    expect(
      screen.queryByRole("checkbox", { name: "Life Insurance" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: "Life Insurance (from company)" }),
    ).toBeInTheDocument();
    expect(
      document.querySelectorAll('input[name="selected_benefits"]'),
    ).toHaveLength(4);
  });

  it("renders KUP type select and its options", () => {
    renderComponent();
    const kupSelect = screen.getByLabelText("Type of Tax-Deductible Costs");
    expect(kupSelect).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Standard (250 PLN/month)" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Elevated (300 PLN/month)" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "50% Creative Work Costs" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "None" })).toBeInTheDocument();
  });

  it("shows/hides creative work percentage input based on KUP type selection", async () => {
    renderComponent();
    const kupSelect = screen.getByLabelText("Type of Tax-Deductible Costs");
    const creativePercentageLabel = i18n.t("form.creative_work_percentage");

    // Initially, creative work percentage input should not be visible
    expect(
      screen.queryByLabelText(creativePercentageLabel),
    ).not.toBeInTheDocument();

    // Select '50% Creative Work Costs'
    fireEvent.change(kupSelect, {
      target: { name: "deductible_cost_settings.type", value: "author_50" },
    });
    await waitFor(() => {
      expect(
        screen.getByLabelText(creativePercentageLabel),
      ).toBeInTheDocument();
    });

    // Select 'Standard' again
    fireEvent.change(kupSelect, {
      target: { name: "deductible_cost_settings.type", value: "standard" },
    });
    await waitFor(() => {
      expect(
        screen.queryByLabelText(creativePercentageLabel),
      ).not.toBeInTheDocument();
    });
  });

  it("updates KUP settings in state correctly", async () => {
    const TestWrapperWithState = () => {
      const [state, dispatch] = useReducer(calculatorReducer, {
        ...initialState,
        b2bData: initialB2bData,
        uopData: {
          monthly_gross_salary: 8000,
          deductible_cost_settings: {
            type: "standard",
            creative_work_percentage: 70,
          },
          youth_relief: false,
          selected_benefits: [],
        },
        loading: false,
        calculationMode: "uop_to_b2b",
      });

      return (
        <CalculatorForm
          state={state}
          dispatch={dispatch}
          handleCalculate={mockOnCalculate}
        />
      );
    };

    render(<TestWrapperWithState />);

    const kupSelect = screen.getByLabelText("Type of Tax-Deductible Costs");
    fireEvent.change(kupSelect, {
      target: { name: "deductible_cost_settings.type", value: "author_50" },
    });
    await waitFor(() => {
      expect(kupSelect).toHaveValue("author_50");
    });

    const creativePercentageInput = screen.getByLabelText(
      "Creative Work Percentage (%)",
    );
    fireEvent.change(creativePercentageInput, {
      target: {
        name: "deductible_cost_settings.creative_work_percentage",
        value: "85",
      },
    });
    await waitFor(() => {
      expect(creativePercentageInput).toHaveValue(85);
    });
  });
});
