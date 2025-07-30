import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { useTranslation } from 'react-i18next';
import { calculateBreakEvenAnalysis } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const BreakEvenChart = ({ b2b, uop }) => {
    const { t } = useTranslation();
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const data = await calculateBreakEvenAnalysis({ b2b, uop });
                const labels = data.map(d => d.b2b_rate);
                const values = data.map(d => d.net_difference);

                setChartData({
                    labels,
                    datasets: [
                        {
                            label: t('break_even.net_difference'),
                            data: values,
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        },
                    ],
                });
            } catch (error) {
                console.error("Error fetching break-even data:", error);
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
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: t('break_even.title'),
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: t('break_even.b2b_rate'),
                },
            },
            y: {
                title: {
                    display: true,
                    text: t('break_even.net_difference_annual'),
                },
                // Add a horizontal line at y=0
                afterBuildTicks: (axis) => {
                    axis.ticks.push({ value: 0, label: 'Próg opłacalności' });
                }
            },
        },
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md mt-6">
            <Line data={chartData} options={options} />
        </div>
    );
};

export default BreakEvenChart;
