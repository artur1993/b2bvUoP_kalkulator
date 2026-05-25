export const initialState = {
  calculationMode: "uop_to_b2b",
  b2bData: {
    monthly_invoice_amount: 10000,
    monthly_business_costs: 500,
    zus_type: "preferential",
    sickness_insurance: false,
    tax_form: "lump_sum_it",
    ip_box_qualified_share: 100,
    ip_box_base_form: "flat_tax",
    vacation_days: 20,
    sick_days: 5,
    stoppage_months: 0,
    age: 30,
    customBenefits: 0,
    companyBenefits: {
      paidVacationDays: { enabled: false, days: 0 },
      paidSickDays: { enabled: false, days: 0 },
      medicalCare: { enabled: false, value: 0 },
      lifeInsurance: { enabled: false, value: 0 },
      sportCard: { enabled: false, value: 0 },
      trainingBudget: { enabled: false, value: 0 },
      otherBenefits: { enabled: false, value: 0 },
    },
  },
  uopData: {
    monthly_gross_salary: 8000,
    deductible_cost_settings: {
      type: "standard",
      creative_work_percentage: 70,
    },
    youth_relief: false,
    selected_benefits: [],
    age: 30,
  },
  results: null,
  loading: false,
  error: null,
};

function updateCompanyBenefit(b2bData, name, value, type, checked) {
  const [benefitType, field] = name.split(".").slice(1);
  return {
    ...b2bData,
    companyBenefits: {
      ...b2bData.companyBenefits,
      [benefitType]: {
        ...b2bData.companyBenefits[benefitType],
        [field]: type === "checkbox" ? checked : value,
      },
    },
  };
}

function updateUopField(uopData, name, value, type, checked) {
  if (name === "selected_benefits") {
    return {
      ...uopData,
      selected_benefits: checked
        ? [...uopData.selected_benefits, value]
        : uopData.selected_benefits.filter((benefit) => benefit !== value),
    };
  }

  if (name.startsWith("deductible_cost_settings.")) {
    const field = name.split(".")[1];
    return {
      ...uopData,
      deductible_cost_settings: {
        ...uopData.deductible_cost_settings,
        [field]: value,
      },
    };
  }

  return {
    ...uopData,
    [name]: type === "checkbox" ? checked : value,
  };
}

export function calculatorReducer(state, action) {
  switch (action.type) {
    case "SET_B2B_FIELD": {
      const { name, value, inputType, checked } = action.payload;
      const b2bData = name.startsWith("companyBenefits.")
        ? updateCompanyBenefit(state.b2bData, name, value, inputType, checked)
        : {
            ...state.b2bData,
            [name]: inputType === "checkbox" ? checked : value,
          };
      return { ...state, b2bData };
    }
    case "SET_UOP_FIELD": {
      const { name, value, inputType, checked } = action.payload;
      return {
        ...state,
        uopData: updateUopField(state.uopData, name, value, inputType, checked),
      };
    }
    case "SET_AGE": {
      const age = action.payload;
      return {
        ...state,
        b2bData: { ...state.b2bData, age },
        uopData: { ...state.uopData, age, youth_relief: age < 26 },
      };
    }
    case "SET_CALCULATION_MODE":
      return { ...state, calculationMode: action.payload };
    case "HYDRATE_FROM_URL":
      return {
        ...state,
        calculationMode:
          action.payload.calculationMode ?? state.calculationMode,
        b2bData: { ...state.b2bData, ...action.payload.b2bData },
        uopData: { ...state.uopData, ...action.payload.uopData },
      };
    case "CALCULATE_START":
      return { ...state, loading: true, error: null };
    case "CALCULATE_SUCCESS":
      return { ...state, loading: false, results: action.payload };
    case "CALCULATE_FAILURE":
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}
