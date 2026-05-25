import React, { useState, forwardRef } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { useTranslation } from 'react-i18next';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const WaterfallChart = forwardRef(({ results }, ref) => {
    const { t } = useTranslation();
    const [contractType, setContractType] = useState('b2b'); // 'b2b' or 'uop'

    if (!results) {
        return <div>{t('loading')}</div>;
    }

    const processData = (steps, type) => {
        if (!steps) return { labels: [], datasets: [] };

        const labels = [];
        const data = [];
        let cumulative = 0;

        if (type === 'b2b') {
            const {
                annual_revenue,
                annual_business_costs,
                pension_insurance_contribution,
                disability_insurance_contribution,
                sickness_insurance_contribution,
                accident_insurance_contribution,
                labor_fund_contribution,
                annual_health_contribution,
                tax_first_threshold,
                tax_second_threshold,
                total_lost_revenue
            } = steps;

            labels.push(t('waterfall.gross_income'));
            data.push([0, annual_revenue]);
            cumulative = annual_revenue;

            labels.push(t('waterfall.costs'));
            data.push([cumulative - annual_business_costs, cumulative]);
            cumulative -= annual_business_costs;
            
            const zusTotal = pension_insurance_contribution + disability_insurance_contribution + sickness_insurance_contribution + accident_insurance_contribution + labor_fund_contribution;
            labels.push(t('waterfall.zus_contributions'));
            data.push([cumulative - zusTotal, cumulative]);
            cumulative -= zusTotal;

            labels.push(t('waterfall.health_contribution'));
            data.push([cumulative - annual_health_contribution, cumulative]);
            cumulative -= annual_health_contribution;

            const taxTotal = tax_first_threshold + tax_second_threshold;
            labels.push(t('waterfall.tax'));
            data.push([cumulative - taxTotal, cumulative]);
            cumulative -= taxTotal;
            
            labels.push(t('waterfall.lost_revenue'));
            data.push([cumulative - total_lost_revenue, cumulative]);
            cumulative -= total_lost_revenue;

            labels.push(t('waterfall.net_income'));
            data.push([0, cumulative]);

        } else { // UoP
            const {
                annual_gross_salary,
                annual_pension_contribution,
                annual_disability_contribution,
                annual_sickness_contribution,
                annual_health_contribution,
                annual_tax
            } = steps;

            labels.push(t('waterfall.gross_salary'));
            data.push([0, annual_gross_salary]);
            cumulative = annual_gross_salary;

            const zusTotal = annual_pension_contribution + annual_disability_contribution + annual_sickness_contribution;
            labels.push(t('waterfall.zus_contributions'));
            data.push([cumulative - zusTotal, cumulative]);
            cumulative -= zusTotal;

            labels.push(t('waterfall.health_contribution'));
            data.push([cumulative - annual_health_contribution, cumulative]);
            cumulative -= annual_health_contribution;

            labels.push(t('waterfall.tax'));
            data.push([cumulative - annual_tax, cumulative]);
            cumulative -= annual_tax;

            labels.push(t('waterfall.net_income'));
            data.push([0, cumulative]);
        }

        return {
            labels,
            datasets: [{
                label: t(`waterfall.title_${contractType}`),
                data: data,
                backgroundColor: (context) => {
                    const value = context.dataset.data[context.dataIndex];
                    if (context.dataIndex === 0) return 'rgba(75, 192, 192, 0.6)'; // Start
                    if (context.dataIndex === data.length - 1) return 'rgba(54, 162, 235, 0.6)'; // End
                    return 'rgba(255, 99, 132, 0.6)'; // Decreases
                },
                borderColor: 'rgba(0,0,0,0.2)',
                borderWidth: 1,
            }]
        };
    };

    const chartData = processData(results[`${contractType}_results`]?.steps, contractType);

    const options = {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: true,
                text: t(`waterfall.title_${contractType}`),
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: t('currency_pln'),
                },
            },
        },
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md mt-6">
            <div className="flex justify-center mb-4">
                <button
                    onClick={() => setContractType('b2b')}
                    className={`px-4 py-2 rounded-l-lg ${contractType === 'b2b' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                    {t('b2b')}
                </button>
                <button
                    onClick={() => setContractType('uop')}
                    className={`px-4 py-2 rounded-r-lg ${contractType === 'uop' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                    {t('uop')}
                </button>
            </div>
            <Bar data={chartData} options={options} ref={ref} />
        </div>
    );
});

export default WaterfallChart;
