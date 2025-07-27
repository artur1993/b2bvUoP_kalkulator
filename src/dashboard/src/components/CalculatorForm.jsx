import React from 'react';
import Input from './Input';
import Select from './Select';
import Checkbox from './Checkbox';

const CalculatorForm = ({ b2bData, uopData, handleB2bChange, handleUopChange, handleCalculate, loading }) => {
  const zusOptions = [
    { value: 'mala_firma', label: 'Mała firma (preferencyjny ZUS)' },
    { value: 'duza_firma', label: 'Duża firma (pełny ZUS)' },
  ];

  const taxFormOptions = [
    { value: 'ryczalt_IT', label: 'Ryczałt IT (12%)' },
    { value: 'liniowy', label: 'Liniowy (19%)' },
    { value: 'skala', label: 'Skala Podatkowa' },
    { value: 'ip_box', label: 'IP Box (5%)' },
  ];

  const benefitOptions = [
    { value: 'opieka_medyczna', label: 'Opieka Medyczna' },
    { value: 'karta_sportowa', label: 'Karta Sportowa' },
    { value: 'ubezpieczenie_na_zycie', label: 'Ubezpieczenie na Życie' },
    { value: 'szkolenia', label: 'Szkolenia' },
    { value: 'ppk', label: 'PPK' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* B2B Section */}
      <div className="bg-gray-50 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">B2B Contract</h2>
        <Input
          label="Monthly Invoice (PLN)"
          id="faktura_miesieczna"
          type="number"
          value={b2bData.faktura_miesieczna}
          onChange={handleB2bChange}
        />
        <Input
          label="Monthly Business Costs (PLN)"
          id="koszty_firmowe_miesieczne"
          type="number"
          value={b2bData.koszty_firmowe_miesieczne}
          onChange={handleB2bChange}
        />
        <Select
          label="ZUS Type"
          id="zus_rodzaj"
          value={b2bData.zus_rodzaj}
          onChange={handleB2bChange}
          options={zusOptions}
        />
        <Checkbox
          label="Voluntary Sick Leave (ZUS Chorobowe)"
          id="zus_chorobowe"
          checked={b2bData.zus_chorobowe}
          onChange={handleB2bChange}
        />
        <Select
          label="Taxation Form"
          id="forma_opodatkowania"
          value={b2bData.forma_opodatkowania}
          onChange={handleB2bChange}
          options={taxFormOptions}
        />
        <Checkbox
          label="Youth Tax Relief (Ulga dla Młodych)"
          id="ulga_dla_mlodych"
          checked={b2bData.ulga_dla_mlodych}
          onChange={handleB2bChange}
        />
        <Input
          label="Annual Vacation Days (unpaid)"
          id="urlop_dni"
          type="number"
          value={b2bData.urlop_dni}
          onChange={handleB2bChange}
        />
        <Input
          label="Annual Sick Days (unpaid)"
          id="chorobowe_dni"
          type="number"
          value={b2bData.chorobowe_dni}
          onChange={handleB2bChange}
        />
        <Input
          label="Months of Stoppage/No Projects"
          id="przestoje_miesiace"
          type="number"
          value={b2bData.przestoje_miesiace}
          onChange={handleB2bChange}
        />
        <Input
          label="Custom Annual Benefits Value (PLN)"
          id="customBenefits"
          type="number"
          value={b2bData.customBenefits}
          onChange={handleB2bChange}
        />

        <h3 className="text-xl font-semibold text-gray-700 mt-6 mb-4">Company Provided Benefits</h3>
        <Checkbox
          label="Paid Vacation Days (from company)"
          id="companyBenefits.paidVacationDays.enabled"
          checked={b2bData.companyBenefits.paidVacationDays.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.paidVacationDays.enabled && (
          <Input
            label="Number of Paid Vacation Days"
            id="companyBenefits.paidVacationDays.days"
            type="number"
            value={b2bData.companyBenefits.paidVacationDays.days}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Paid Sick Days (from company)"
          id="companyBenefits.paidSickDays.enabled"
          checked={b2bData.companyBenefits.paidSickDays.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.paidSickDays.enabled && (
          <Input
            label="Number of Paid Sick Days"
            id="companyBenefits.paidSickDays.days"
            type="number"
            value={b2bData.companyBenefits.paidSickDays.days}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Medical Care (from company)"
          id="companyBenefits.medicalCare.enabled"
          checked={b2bData.companyBenefits.medicalCare.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.medicalCare.enabled && (
          <Input
            label="Medical Care Value (PLN/year)"
            id="companyBenefits.medicalCare.value"
            type="number"
            value={b2bData.companyBenefits.medicalCare.value}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Life Insurance (from company)"
          id="companyBenefits.lifeInsurance.enabled"
          checked={b2bData.companyBenefits.lifeInsurance.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.lifeInsurance.enabled && (
          <Input
            label="Life Insurance Value (PLN/year)"
            id="companyBenefits.lifeInsurance.value"
            type="number"
            value={b2bData.companyBenefits.lifeInsurance.value}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Sport Card (from company)"
          id="companyBenefits.sportCard.enabled"
          checked={b2bData.companyBenefits.sportCard.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.sportCard.enabled && (
          <Input
            label="Sport Card Value (PLN/year)"
            id="companyBenefits.sportCard.value"
            type="number"
            value={b2bData.companyBenefits.sportCard.value}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Training Budget (from company)"
          id="companyBenefits.trainingBudget.enabled"
          checked={b2bData.companyBenefits.trainingBudget.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.trainingBudget.enabled && (
          <Input
            label="Training Budget Value (PLN/year)"
            id="companyBenefits.trainingBudget.value"
            type="number"
            value={b2bData.companyBenefits.trainingBudget.value}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
        <Checkbox
          label="Other Benefits (from company)"
          id="companyBenefits.otherBenefits.enabled"
          checked={b2bData.companyBenefits.otherBenefits.enabled}
          onChange={handleB2bChange}
        />
        {b2bData.companyBenefits.otherBenefits.enabled && (
          <Input
            label="Other Benefits Value (PLN/year)"
            id="companyBenefits.otherBenefits.value"
            type="number"
            value={b2bData.companyBenefits.otherBenefits.value}
            onChange={handleB2bChange}
            className="ml-6"
          />
        )}
      </div>

      {/* UoP Section */}
      <div className="bg-gray-50 p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Employment Contract (UoP)</h2>
        <Input
          label="Gross Monthly Salary (PLN)"
          id="wynagrodzenie_brutto"
          type="number"
          value={uopData.wynagrodzenie_brutto}
          onChange={handleUopChange}
        />
        <Input
          label="Annual Tax-Deductible Costs (PLN)"
          id="koszty_uzyskania_przychodu"
          type="number"
          value={uopData.koszty_uzyskania_przychodu}
          onChange={handleUopChange}
        />
        <Checkbox
          label="Youth Tax Relief (Ulga dla Młodych)"
          id="ulga_dla_mlodych"
          checked={uopData.ulga_dla_mlodych}
          onChange={handleUopChange}
        />

        <h3 className="text-xl font-semibold text-gray-700 mt-6 mb-4">Selected Benefits</h3>
        {benefitOptions.map((option) => (
          <Checkbox
            key={option.value}
            label={option.label}
            id={option.value}
            name="wybrane_benefity"
            value={option.value}
            checked={uopData.wybrane_benefity.includes(option.value)}
            onChange={handleUopChange}
          />
        ))}
      </div>

      <div className="md:col-span-2 flex justify-center mt-8">
        <button
          onClick={handleCalculate}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg text-xl transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-75"
        >
          {loading ? 'Calculating...' : 'Calculate Comparison'}
        </button>
      </div>
    </div>
  );
};

export default CalculatorForm;