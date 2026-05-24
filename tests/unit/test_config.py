from src.config import config_manager


def test_config_loads_with_metadata():
    config = config_manager.get_config()

    assert config['zus_2026']['full']['pension'] == 1103.27
    assert config['ppk']['employee_rate'] == 0.02
    assert '_meta' in config


def test_config_has_metadata_for_all_regulatory_branches():
    config = config_manager.get_config()
    meta = config['_meta']
    regulatory_branches = [
        'macro_indicators_2026',
        'tax_thresholds',
        'tax_thresholds.health_contribution_deduction_limit_flat_tax',
        'tax_deductible_costs',
        'zus_2026',
        'zus_2026.health_lump_sum_thresholds',
        'zus_2026.minimum_health_annual_2026',
        'pension_limits_2026.ike',
        'pension_limits_2026.ikze',
        'ppk',
        'uop_days_off',
    ]
    required_fields = {'source_url', 'source_checked_at', 'valid_from', 'valid_to'}

    for branch in regulatory_branches:
        assert branch in meta
        assert required_fields <= set(meta[branch])
        assert meta[branch]['source_url'].startswith('https://')
        assert meta[branch]['source_checked_at'] == '2026-05-23'
