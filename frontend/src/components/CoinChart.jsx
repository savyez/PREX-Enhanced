import { useEffect, useState } from 'react';
import SparklineChart from './SparklineChart.jsx';
import { chart_data } from '../utils/api.js';

function CoinChart({ coin, height = 84 }) {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isActive = true;

        const loadChart = async () => {
            if (!coin) {
                return;
            }

            setLoading(true);
            setError(null);

            try {
                const response = await chart_data(coin.coin_name || coin.ticker || '', 7);
                const normalized = (response?.chart_data || [])
                    .map((point) => ({
                        ...point,
                        price: Number(point.price),
                    }))
                    .filter((point) => Number.isFinite(point.price));

                if (isActive) {
                    setChartData(normalized);
                }
            } catch (err) {
                if (isActive) {
                    setError(err.message || 'Trend unavailable');
                    setChartData([]);
                }
            } finally {
                if (isActive) {
                    setLoading(false);
                }
            }
        };

        loadChart();

        return () => {
            isActive = false;
        };
    }, [coin?.coin_name, coin?.ticker]);

    if (!coin) {
        return null;
    }

    return (
        <div className="coin-sparkline" aria-label={`${coin.coin_name} price trend`}>
            <SparklineChart
                data={chartData}
                loading={loading}
                error={error}
                chartId={coin.ticker || coin.coin_name}
                height={height}
                compact
            />
        </div>
    );
}

export default CoinChart;
