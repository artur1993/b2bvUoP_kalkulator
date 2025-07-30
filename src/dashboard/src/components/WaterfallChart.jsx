import React, { useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { useTranslation } from 'react-i18next';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const WaterfallChart = ({ results }) => {
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
                'Przychód roczny': przychod,
                'Koszty firmowe roczne': koszty,
                skladki_zus_emerytalna,
                skladki_zus_rentowa,
                skladki_zus_chorobowa,
                skladka_zdrowotna,
                podatek_prog_1,
                podatek_prog_2,
                'Utracony przychód': utraconyPrzychod
            } = steps;

            labels.push(t('waterfall.gross_income'));
            data.push([0, przychod]);
            cumulative = przychod;

            labels.push(t('waterfall.costs'));
            data.push([cumulative - koszty, cumulative]);
            cumulative -= koszty;
            
            const zusTotal = skladki_zus_emerytalna + skladki_zus_rentowa + skladki_zus_chorobowa;
            labels.push(t('waterfall.zus_contributions'));
            data.push([cumulative - zusTotal, cumulative]);
            cumulative -= zusTotal;

            labels.push(t('waterfall.health_contribution'));
            data.push([cumulative - skladka_zdrowotna, cumulative]);
            cumulative -= skladka_zdrowotna;

            const taxTotal = podatek_prog_1 + podatek_prog_2;
            labels.push(t('waterfall.tax'));
            data.push([cumulative - taxTotal, cumulative]);
            cumulative -= taxTotal;
            
            labels.push(t('waterfall.lost_revenue'));
            data.push([cumulative - utraconyPrzychod, cumulative]);
            cumulative -= utraconyPrzychod;

            labels.push(t('waterfall.net_income'));
            data.push([0, cumulative]);

        } else { // UoP
            const {
                'Roczne wynagrodzenie brutto': brutto,
                skladki_zus_emerytalna,
                skladki_zus_rentowa,
                skladki_zus_chorobowa,
                skladka_zdrowotna,
                podatek_prog_1,
                podatek_prog_2,
            } = steps;

            labels.push(t('waterfall.gross_salary'));
            data.push([0, brutto]);
            cumulative = brutto;

            const zusTotal = skladki_zus_emerytalna + skladki_zus_rentowa + skladki_zus_chorobowa;
            labels.push(t('waterfall.zus_contributions'));
            data.push([cumulative - zusTotal, cumulative]);
            cumulative -= zusTotal;

            labels.push(t('waterfall.health_contribution'));
            data.push([cumulative - skladka_zdrowotna, cumulative]);
            cumulative -= skladka_zdrowotna;

            const taxTotal = podatek_prog_1 + podatek_prog_2;
            labels.push(t('waterfall.tax'));
            data.push([cumulative - taxTotal, cumulative]);
            cumulative -= taxTotal;

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
            <Bar data={chartData} options={options} />
        </div>
    );
};

export default WaterfallChart;
