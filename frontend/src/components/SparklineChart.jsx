import { useMemo } from 'react';
import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

function SparklineChart({
    data = [],
    loading = false,
    error = null,
    title = 'Price Trend',
    chartId,
    height = 220,
    showAxes = false,
    compact = false,
}) {
    const chartDomain = useMemo(() => {
        if (!data.length) {
            return [0, 1];
        }

        const prices = data.map((point) => point.price);
        const min = Math.min(...prices);
        const max = Math.max(...prices);

        if (min === max) {
            return [min * 0.999, max * 1.001];
        }

        return [min, max];
    }, [data]);

    if (data.length > 1) {
        return (
            <div className={`sparkline-chart ${compact ? 'sparkline-chart--compact' : ''}`}>
                {title && <div className="chart-heading">{title}</div>}
                <ResponsiveContainer width="100%" height={height}>
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id={`sparkline-gradient-${chartId}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.45} />
                                <stop offset="100%" stopColor="#60a5fa" stopOpacity={0.05} />
                            </linearGradient>
                        </defs>
                        {showAxes && <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />}
                        <XAxis
                            dataKey="timestamp"
                            hide={!showAxes}
                            tick={{ fill: '#aeb9c9', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            tickLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            label={showAxes ? { value: 'Time', position: 'insideBottom', offset: -8, fill: '#94a3b8' } : undefined}
                        />
                        <YAxis
                            hide={!showAxes}
                            domain={chartDomain}
                            tick={{ fill: '#aeb9c9', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            tickLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            label={showAxes ? {
                                value: 'Price (USD)',
                                angle: -90,
                                position: 'insideLeft',
                                fill: '#94a3b8',
                                offset: 10,
                            } : undefined}
                        />
                        <Tooltip
                            formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Price']}
                            labelFormatter={(label) => new Date(label).toLocaleString()}
                            contentStyle={{
                                background: '#111827',
                                border: '1px solid rgba(255,255,255,0.12)',
                                borderRadius: '12px',
                                color: '#e5e7eb',
                            }}
                        />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke="#60a5fa"
                            strokeWidth={2}
                            fill={`url(#sparkline-gradient-${chartId})`}
                            dot={false}
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        );
    }

    const placeholderText = loading
        ? 'Loading trend...'
        : error
            ? 'Trend unavailable'
            : 'No trend data';

    return (
        <div className="coin-sparkline-placeholder">
            {placeholderText}
        </div>
    );
}

export default SparklineChart;
