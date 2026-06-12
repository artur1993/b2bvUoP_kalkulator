import unittest

from backend.calculations import (
    calculate_b2b_results,
    calculate_uop_results,
    compute_solidarity_tax,
)
from backend.config import config_manager


def test_solidarity_tax_below_threshold():
    assert compute_solidarity_tax(500000, config_manager.get_config()) == 0


def test_solidarity_tax_at_threshold():
    assert compute_solidarity_tax(1000000, config_manager.get_config()) == 0


def test_solidarity_tax_above_threshold():
    assert compute_solidarity_tax(1200000, config_manager.get_config()) == 8000


def _high_income_b2b_data(tax_form, **overrides):
    data = {
        "monthly_invoice_amount": 100000,
        "monthly_business_costs": 0,
        "zus_type": "full",
        "sickness_insurance": False,
        "tax_form": tax_form,
        "vacation_days": 0,
        "sick_days": 0,
        "stoppage_months": 0,
        "customBenefits": 0,
        "companyBenefits": {},
    }
    data.update(overrides)
    return data


def test_b2b_lump_sum_high_income_excludes_solidarity_tax_negative():
    # Przychody ryczałtowe nie wchodzą do podstawy daniny (art. 30h ust. 2 PIT).
    results = calculate_b2b_results(_high_income_b2b_data("lump_sum_it"))

    assert results["annual_solidarity_tax"] == 0


def test_b2b_flat_tax_high_income_includes_solidarity_tax_positive():
    results = calculate_b2b_results(_high_income_b2b_data("flat_tax"))

    # Podstawa daniny = dochód − składki społeczne (bez odliczenia zdrowotnej):
    # 1 200 000 − 21 459,48 = 1 178 540,52 → 4% nadwyżki ponad 1 mln = 7 141,62.
    assert abs(results["annual_solidarity_tax"] - 7141.62) < 0.01
    assert results["annual_tax"] > results["annual_solidarity_tax"]


def test_b2b_ip_box_qualified_income_excludes_solidarity_tax_negative():
    # Dochód z kwalifikowanych IP (art. 30ca) nie jest objęty daniną.
    results = calculate_b2b_results(
        _high_income_b2b_data(
            "ip_box", ip_box_qualified_share=100, ip_box_base_form="flat_tax"
        )
    )

    assert results["annual_solidarity_tax"] == 0


class TestCalculations(unittest.TestCase):
    def test_calculate_b2b_results_english_keys(self):
        b2b_data = {
            "monthly_invoice_amount": 10000,
            "monthly_business_costs": 1000,
            "zus_type": "full",
            "sickness_insurance": True,
            "tax_form": "flat_tax",
            "vacation_days": 20,
            "sick_days": 10,
            "stoppage_months": 1,
            "customBenefits": 100,
            "companyBenefits": {},
        }
        results = calculate_b2b_results(b2b_data)
        self.assertIn("total_annual_value", results)
        self.assertNotIn("calkowita_roczna_wartosc", results)

    def test_calculate_uop_results_english_keys(self):
        uop_data = {
            "monthly_gross_salary": 10000,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "youth_relief": False,
            "selected_benefits": [],
        }
        results = calculate_uop_results(uop_data)
        self.assertIn("total_annual_value", results)
        self.assertNotIn("calkowita_roczna_wartosc", results)

    def _b2b_lump_sum_data(self, monthly_invoice_amount):
        return {
            "monthly_invoice_amount": monthly_invoice_amount,
            "monthly_business_costs": 0,
            "zus_type": "full",
            "sickness_insurance": False,
            "tax_form": "lump_sum_it",
            "vacation_days": 0,
            "sick_days": 0,
            "stoppage_months": 0,
            "customBenefits": 0,
            "companyBenefits": {},
        }

    def test_health_contribution_lump_sum_threshold_60k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5000))

        self.assertAlmostEqual(
            results["steps"]["annual_health_contribution"] / 12, 498.35, places=2
        )

    def test_calculate_with_start_relief_zus(self):
        data = self._b2b_lump_sum_data(10000)
        data["zus_type"] = "start_relief"

        results = calculate_b2b_results(data)

        self.assertEqual(results["steps"]["annual_social_contributions"], 0)
        self.assertAlmostEqual(
            results["steps"]["annual_health_contribution"], 830.58 * 12, places=2
        )

    def test_health_contribution_lump_sum_threshold_60k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(5001))

        self.assertAlmostEqual(
            results["steps"]["annual_health_contribution"] / 12, 830.58, places=2
        )

    def test_health_contribution_lump_sum_threshold_300k(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25000))

        self.assertAlmostEqual(
            results["steps"]["annual_health_contribution"] / 12, 830.58, places=2
        )

    def test_health_contribution_lump_sum_threshold_300k_plus_1(self):
        results = calculate_b2b_results(self._b2b_lump_sum_data(25001))

        self.assertAlmostEqual(
            results["steps"]["annual_health_contribution"] / 12, 1495.04, places=2
        )

    def test_minimum_health_annual_2026(self):
        data = self._b2b_lump_sum_data(0)
        data["tax_form"] = "flat_tax"

        results = calculate_b2b_results(data)

        self.assertAlmostEqual(results["steps"]["annual_health_contribution"], 5072.90, places=2)

    def test_pit_0_not_applied_to_b2b(self):
        data = self._b2b_lump_sum_data(12000)
        data.update(
            {
                "tax_form": "flat_tax",
                "age": 24,
                "youth_relief": True,
            }
        )

        results = calculate_b2b_results(data)

        self.assertEqual(results["annual_tax"], 22142)

    def test_ip_box_100_percent_qualified(self):
        data = self._b2b_lump_sum_data(10000)
        data.update(
            {
                "tax_form": "ip_box",
                "ip_box_qualified_share": 100,
                "ip_box_base_form": "flat_tax",
            }
        )

        results = calculate_b2b_results(data)

        self.assertEqual(results["annual_tax"], 4927)

    def test_ip_box_60_percent_qualified_flat_base(self):
        data = self._b2b_lump_sum_data(10000)
        data.update(
            {
                "tax_form": "ip_box",
                "ip_box_qualified_share": 60,
                "ip_box_base_form": "flat_tax",
            }
        )

        results = calculate_b2b_results(data)

        self.assertEqual(results["annual_tax"], 10445)

    def test_ip_box_60_percent_qualified_scale_base(self):
        data = self._b2b_lump_sum_data(10000)
        data.update(
            {
                "tax_form": "ip_box",
                "ip_box_qualified_share": 60,
                "ip_box_base_form": "tax_scale",
            }
        )

        results = calculate_b2b_results(data)

        self.assertEqual(results["annual_tax"], 4086)

    def test_uop_total_value_without_double_vacation(self):
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 10000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": False,
                "selected_benefits": [],
            }
        )
        removed_key = "annual_paid_days_off_" + "value"
        former_paid_days_off_amount = 26 * (10000 / 21)

        self.assertAlmostEqual(
            results["total_annual_value"], results["annual_net_income"], delta=50
        )
        self.assertNotIn(removed_key, results)
        self.assertAlmostEqual(
            results["annual_net_income"]
            + former_paid_days_off_amount
            - results["total_annual_value"],
            former_paid_days_off_amount,
            places=2,
        )

    def test_ppk_employee_contribution_lowers_net(self):
        base_data = {
            "monthly_gross_salary": 10000,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "youth_relief": False,
            "selected_benefits": [],
        }
        without_ppk = calculate_uop_results(base_data)
        with_ppk = calculate_uop_results({**base_data, "selected_benefits": ["ppk"]})
        monthly_cash_difference = (
            without_ppk["annual_net_income"] - with_ppk["annual_net_income"]
        ) / 12

        self.assertGreater(without_ppk["annual_net_income"], with_ppk["annual_net_income"])
        self.assertGreater(monthly_cash_difference, 180)
        self.assertLess(monthly_cash_difference, 260)
        self.assertAlmostEqual(
            with_ppk["steps"]["annual_ppk_employee_contribution"], 2400, places=2
        )

    def test_youth_relief_below_limit_fully_exempts_revenue_positive(self):
        # 84 000 przychodu < 85 528: całość zwolniona, zero podstawy i podatku.
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 7000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": True,
                "selected_benefits": [],
            }
        )

        self.assertEqual(results["annual_tax"], 0)
        self.assertEqual(results["steps"]["tax_breakdown"]["annual_taxable_base"], 0)
        # KUP przysługują tylko od przychodu opodatkowanego — tu brak.
        self.assertEqual(results["steps"]["annual_deductible_costs"], 0)

    def test_youth_relief_exempts_revenue_not_income_positive(self):
        # 180 000 przychodu: zwolnione 85 528 PRZYCHODU. Od nadwyżki odliczalne są
        # tylko składki na nią przypadające (art. 26 ust. 1 pkt 2) i KUP za miesiące
        # z przychodem opodatkowanym: podstawa = 94 472 − 12 952,11 − 1 750 ≈ 79 770.
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 15000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": True,
                "selected_benefits": [],
            }
        )

        self.assertAlmostEqual(
            results["steps"]["tax_breakdown"]["annual_taxable_base"], 79769.90, delta=1
        )
        self.assertAlmostEqual(results["annual_tax"], 5973, delta=2)

    def test_youth_relief_covers_bonus_within_limit_positive(self):
        # Pensja 72 000 + premia 7 200 < 85 528: premia bez PIT, ale ze składkami.
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 6000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": True,
                "selected_benefits": [],
                "annual_bonus_pct": 10,
            }
        )
        bonus = results["steps"]["bonus_breakdown"]

        self.assertEqual(bonus["tax"], 0)
        self.assertGreater(bonus["social_contributions"], 0)
        self.assertGreater(bonus["health_contribution"], 0)

    def test_annual_bonus_is_subject_to_zus_and_health_positive(self):
        base_data = {
            "monthly_gross_salary": 10000,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "youth_relief": False,
            "selected_benefits": [],
        }
        results = calculate_uop_results({**base_data, "annual_bonus_pct": 10})
        bonus = results["steps"]["bonus_breakdown"]

        # 12 000 premii: społeczne 13,71% = 1 645,20; zdrowotna 9% od pomniejszonej
        # bazy = 931,93; PIT marginalny 12% od dochodu z premii.
        self.assertAlmostEqual(results["annual_bonus_gross"], 12000, places=2)
        self.assertAlmostEqual(bonus["social_contributions"], 12000 * 0.1371, places=2)
        self.assertAlmostEqual(
            bonus["health_contribution"], (12000 - 12000 * 0.1371) * 0.09, places=2
        )
        self.assertAlmostEqual(bonus["tax"], 1243, delta=2)
        self.assertAlmostEqual(
            results["annual_bonus_net"],
            12000 - bonus["social_contributions"] - bonus["health_contribution"] - bonus["tax"],
            places=2,
        )
        # Netto z premii to mniej niż ~75% brutto premii (ZUS + zdrowotna + PIT).
        self.assertLess(results["annual_bonus_net"], 12000 * 0.75)

    def test_annual_bonus_respects_thirty_times_limit_neutral(self):
        # 25 000/mies. = 300 000 rocznie > 282 600: limit emerytalno-rentowej
        # wyczerpany pensją zasadniczą, od premii tylko chorobowa (2,45%).
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 25000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": False,
                "selected_benefits": [],
                "annual_bonus_pct": 10,
            }
        )
        bonus = results["steps"]["bonus_breakdown"]

        self.assertAlmostEqual(bonus["social_contributions"], bonus["gross"] * 0.0245, places=2)

    def test_ppk_employee_contribution_does_not_reduce_tax_base_positive(self):
        base_data = {
            "monthly_gross_salary": 10000,
            "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
            "youth_relief": False,
            "selected_benefits": [],
        }
        without_ppk = calculate_uop_results(base_data)
        with_ppk = calculate_uop_results({**base_data, "selected_benefits": ["ppk"]})

        # Wpłata pracownika (2%) jest z netto — podatkowo neutralna. Jedyna różnica
        # w PIT to opodatkowanie wpłaty pracodawcy (1800 zł × 12% = 216 zł).
        self.assertAlmostEqual(with_ppk["annual_tax"] - without_ppk["annual_tax"], 216, delta=1)
        self.assertAlmostEqual(
            with_ppk["steps"]["tax_breakdown"]["annual_taxable_base"]
            - without_ppk["steps"]["tax_breakdown"]["annual_taxable_base"],
            with_ppk["steps"]["annual_ppk_employer_contribution"],
            places=2,
        )

    def test_ppk_employer_contribution_is_taxed_benefit(self):
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 10000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": False,
                "selected_benefits": ["ppk"],
            }
        )

        self.assertAlmostEqual(results["steps"]["annual_ppk_employer_contribution"], 1800, places=2)
        self.assertAlmostEqual(results["steps"]["annual_ppk_employer_net"], 1584, delta=50)
        # PPK nie jest już doliczane do "benefitów" (karta/medyk) — jest osobnym kapitałem.
        self.assertEqual(results["annual_benefits_value"], 0)
        # Dopłata roczna państwa.
        self.assertAlmostEqual(results["steps"]["annual_ppk_state_subsidy"], 240, places=2)
        # Kapitał PPK = wpłata pracownika (2%) + pracodawcy netto po PIT + dopłata państwa.
        # employer_net ≈ 1584 (1800 brutto minus ~216 PIT), total ≈ 4224.
        employer_net = results["steps"]["annual_ppk_employer_net"]
        self.assertAlmostEqual(
            results["annual_ppk_capital"],
            2400 + employer_net + 240,
            places=2,
        )
        # Cała wartość PPK ponad netto to właśnie kapitał (brak innych benefitów/custom).
        self.assertAlmostEqual(
            results["total_annual_value"] - results["annual_net_income"],
            results["annual_ppk_capital"],
            places=2,
        )

    def test_ppk_disabled_no_changes(self):
        results = calculate_uop_results(
            {
                "monthly_gross_salary": 10000,
                "deductible_cost_settings": {"type": "standard", "creative_work_percentage": 0},
                "youth_relief": False,
                "selected_benefits": [],
            }
        )

        self.assertEqual(results["annual_benefits_value"], 0)
        self.assertEqual(results["annual_ppk_capital"], 0)
        self.assertEqual(results["steps"]["annual_ppk_employee_contribution"], 0)
        self.assertEqual(results["steps"]["annual_ppk_employer_contribution"], 0)
        self.assertEqual(results["steps"]["annual_ppk_employer_net"], 0)
        self.assertEqual(results["steps"]["annual_ppk_state_subsidy"], 0)


if __name__ == "__main__":
    unittest.main()
