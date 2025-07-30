import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, IndexAxis } from 'chart.js';
import { useTranslation } from 'react-i18next';
import { calculateSensitivityAnalysis } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const SensitivityChart = ({ b2b, uop }) => {
    const { t } = useTranslation();
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const data = await calculateSensitivityAnalysis({ b2b, uop });
                // Sort data by impact
                data.sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

                const labels = data.map(d => t(`sensitivity.${d.parameter}`));
                const values = data.map(d => d.impact);

                setChartData({
                    labels,
                    datasets: [
                        {
                            label: t('sensitivity.impact_on_net'),
                            data: values,
                            backgroundColor: 'rgba(255, 159, 64, 0.6)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1,
                        },
                    ],
                });
            } catch (error) {
                console.error("Error fetching sensitivity data:", error);
            } finally {
                setLoading(false);
            }
        };

        if (b2b && uop) {
            fetchData();
        }
    }, [b2b, uop, t]);

    if (loading) {
        return <div>{t('loading')}</div>;
    }

    if (!chartData) {
        return <div>{t('no_data')}</div>;
    }

    const options = {
        indexAxis: 'y', // This makes the bar chart horizontal
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: true,
                text: t('sensitivity.title'),
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: t('sensitivity.impact_on_net_annual'),
                },
            },
        },
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md mt-6">
            <Bar data={chartData} options={options} />
        </div>
    );
};

export default SensitivityChart;
