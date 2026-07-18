import { useEffect, useState } from 'react';
import SparklineChart from './SparklineChart.jsx';
import { chart_data } from '../utils/api.js';

const normalizeChartPoints = (points = []) =>
    (points || [])
        .map((point) => ({
            ...point,
            price: Number(point.price),
        }))
        .filter((point) => Number.isFinite(point.price));

const getCoinChartKey = (coin) => coin?.ticker || coin?.coin_name || '';

function CoinChart({ coin, height = 84, showAxes = false, hidden = false }) {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isActive = true;

        if (!coin) {
            setChartData([]);
            setLoading(false);
            setError(null);
            return () => {
                isActive = false;
            };
        }
        if (hidden) {
            // If chart is hidden, don't fetch data.
            setChartData([]);
            setLoading(false);
            setError(null);
            return () => {
                isActive = false;
            };
        }
        const loadChart = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await chart_data(getCoinChartKey(coin), 7);
                const normalized = normalizeChartPoints(response?.chart_data);

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
    }, [coin, hidden]);

    if (!coin) {
        return null;
    }

    return (
        <SparklineChart
            className="coin-sparkline"
            ariaLabel={`${coin.coin_name || coin.ticker} price trend`}
            data={chartData}
            loading={loading}
            error={error}
            chartId={getCoinChartKey(coin)}
            height={height}
            compact={height <= 84}
            showAxes={showAxes}
            title="Price Trend"
        />
    );
}

export default CoinChart;
