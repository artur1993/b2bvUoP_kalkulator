// New file: src/data/insuranceOptions.js

export const insuranceModules = {
  income_protection: {
    name: "Ubezpieczenie od utraty dochodu",
    tooltip: "UoP daje 80% wynagrodzenia automatycznie. Wybierz poziom pokrycia dla B2B, aby zabezpieczyć się na wypadek choroby lub wypadku uniemożliwiającego pracę.",
    type: "dynamic",
    options: {
      basic: { coverage: 50, multiplier: 0.008, details: "Świadczenie: 50% dochodu", uop_comparison: "UoP zapewnia 80%" },
      standard: { coverage: 65, multiplier: 0.012, details: "Świadczenie: 65% dochodu", uop_comparison: "UoP zapewnia 80%" },
      uop_equivalent: { coverage: 80, multiplier: 0.015, details: "Świadczenie: 80% dochodu", uop_comparison: "Poziom identyczny z UoP" },
      premium: { coverage: 100, multiplier: 0.020, details: "Świadczenie: 100% dochodu", uop_comparison: "Poziom wyższy niż UoP" }
    },
    default: "uop_equivalent",
    weight: 50
  },
  professional_liability: {
    name: "OC zawodowe",
    tooltip: "W UoP Twoja odpowiedzialność za błędy jest ograniczona do 3 pensji. Na B2B ryzykujesz całym majątkiem. To ubezpieczenie chroni Cię przed roszczeniami klientów.",
    type: "fixed",
    options: {
      basic: { cost: 33.33, details: "Suma ubezpieczenia: 500 000 zł", uop_comparison: "UoP: odp. do 3 pensji" },
      standard: { cost: 66.67, details: "Suma ubezpieczenia: 1 000 000 zł", uop_comparison: "UoP: odp. do 3 pensji" },
      premium: { cost: 125, details: "Suma ubezpieczenia: 2 000 000 zł", uop_comparison: "UoP: odp. do 3 pensji" }
    },
    default: "standard",
    weight: 25
  },
  private_health: {
    name: "Prywatne zdrowotne",
    tooltip: "UoP często zapewnia pakiet medyczny w standardzie. Na B2B musisz samodzielnie zadbać o szybki dostęp do specjalistów i badań.",
    type: "fixed",
    options: {
      basic: { cost: 150, details: "Podstawowy pakiet, dostęp do lekarza rodzinnego", uop_comparison: "UoP: pakiet podstawowy" },
      standard: { cost: 300, details: "Rozszerzony pakiet, dostęp do specjalistów", uop_comparison: "UoP: pakiet standardowy" },
      premium: { cost: 500, details: "Pełny pakiet, szeroki zakres usług", uop_comparison: "UoP: pakiet premium" }
    },
    default: "standard",
    weight: 15
  },
  equipment: {
    name: "Ubezpieczenie sprzętu",
    tooltip: "Ubezpieczenie Twojego komputera i innego sprzętu firmowego od kradzieży lub uszkodzenia.",
    type: "fixed",
    options: {
      basic: { cost: 50, details: "Suma ubezpieczenia: 5 000 zł", uop_comparison: "UoP: sprzęt firmy" },
      standard: { cost: 100, details: "Suma ubezpieczenia: 10 000 zł", uop_comparison: "UoP: sprzęt firmy" },
      premium: { cost: 200, details: "Suma ubezpieczenia: 20 000 zł", uop_comparison: "UoP: sprzęt firmy" }
    },
    default: "standard",
    weight: 5
  },
  zus_voluntary: {
    name: "ZUS dobrowolne",
    tooltip: "Zapewnia prawo do zasiłku chorobowego i macierzyńskiego z ZUS, którego standardowo nie ma na B2B.",
    type: "fixed",
    options: {
      enabled: { cost: 34.30, details: "Prawo do zasiłku chorobowego i macierzyńskiego", uop_comparison: "UoP: obowiązkowe" }
    },
    default: "enabled",
    weight: 2
  },
  legal_protection: {
    name: "Ochrona prawna",
    tooltip: "Dostęp do porad prawnych i pokrycie kosztów sądowych w sporach z klientami lub urzędami.",
    type: "fixed",
    options: {
      basic: { cost: 30, details: "Podstawowe doradztwo prawne", uop_comparison: "UoP: wsparcie działu prawnego" },
      standard: { cost: 60, details: "Rozszerzone wsparcie prawne, pokrycie kosztów sądowych", uop_comparison: "UoP: wsparcie działu prawnego" }
    },
    default: "basic",
    weight: 2
  },
  cyber_insurance: {
    name: "Ubezpieczenie cyber",
    tooltip: "Ochrona przed skutkami ataków hakerskich, wycieków danych i innych zagrożeń cybernetycznych.",
    type: "fixed",
    options: {
      basic: { cost: 50, details: "Ochrona przed atakami hakerskimi, odzyskiwanie danych", uop_comparison: "UoP: ochrona firmy" },
      standard: { cost: 100, details: "Rozszerzona ochrona, wsparcie w przypadku wycieku danych", uop_comparison: "UoP: ochrona firmy" }
    },
    default: "basic",
    weight: 1
  }
};

export const insuranceProfiles = {
  minimal: {
    income_protection: { enabled: true, level: "basic" },
    professional_liability: { enabled: true, level: "basic" },
    private_health: { enabled: false, level: "basic" },
    equipment: { enabled: false, level: "basic" },
    zus_voluntary: { enabled: true, level: "enabled" },
    legal_protection: { enabled: false, level: "basic" },
    cyber_insurance: { enabled: false, level: "basic" }
  },
  standard: {
    income_protection: { enabled: true, level: "uop_equivalent" },
    professional_liability: { enabled: true, level: "standard" },
    private_health: { enabled: true, level: "standard" },
    equipment: { enabled: true, level: "standard" },
    zus_voluntary: { enabled: true, level: "enabled" },
    legal_protection: { enabled: true, level: "basic" },
    cyber_insurance: { enabled: false, level: "basic" }
  },
  premium: {
    income_protection: { enabled: true, level: "premium" },
    professional_liability: { enabled: true, level: "premium" },
    private_health: { enabled: true, level: "premium" },
    equipment: { enabled: true, level: "premium" },
    zus_voluntary: { enabled: true, level: "enabled" },
    legal_protection: { enabled: true, level: "standard" },
    cyber_insurance: { enabled: true, level: "standard" }
  }
};