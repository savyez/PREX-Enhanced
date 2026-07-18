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
    chartId = 'sparkline',
    height = 220,
    showAxes = false,
    compact = false,
    className = '',
    ariaLabel,
}) {
    const formattedData = useMemo(
        () =>
            (data || [])
                .map((point) => ({
                    ...point,
                    price: Number(point.price),
                }))
                .filter((point) => Number.isFinite(point.price)),
        [data]
    );

    const chartDomain = useMemo(() => {
        if (formattedData.length === 0) {
            return [0, 1];
        }

        const prices = formattedData.map((point) => point.price);
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        const range = Math.max(max - min, Math.abs(min) * 0.003, 0.0001);
        const padding = range * 0.12;
        const lower = min <= 0 ? 0 : min - padding;
        const upper = max + padding;

        return [lower, upper];
    }, [formattedData]);

    const trendColor = useMemo(() => {
        if (formattedData.length < 2) {
            return '#60a5fa';
        }

        const first = formattedData[0].price;
        const last = formattedData[formattedData.length - 1].price;

        return last === first ? '#94a3b8' : last > first ? '#22c55e' : '#ef4444';
    }, [formattedData]);

    const placeholderText = loading
        ? 'Loading trend...'
        : error
        ? 'Trend unavailable'
        : 'No trend data';

    return (
        <div
            className={`sparkline-chart ${compact ? 'sparkline-chart--compact' : ''}${className ? ` ${className}` : ''}`}
            aria-label={ariaLabel}
        >
            {title && <div className="chart-heading">{title}</div>}

            {formattedData.length > 1 ? (
                <ResponsiveContainer width="100%" height={height}>
                    <AreaChart
                        data={formattedData}
                        margin={
                            showAxes
                                ? { top: 10, right: 60, bottom: 4, left: 20 }
                                : { top: 4, right: 4, bottom: 4, left: 4 }
                        }
                    >
                        <defs>
                            <linearGradient id={`sparkline-gradient-${chartId}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={trendColor} stopOpacity={0.45} />
                                <stop offset="100%" stopColor={trendColor} stopOpacity={0.05} />
                            </linearGradient>
                        </defs>

                        {showAxes && <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />}

                        <XAxis
                            dataKey="timestamp"
                            hide={!showAxes}
                            tick={{ fill: '#aeb9c9', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            tickLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            tickMargin={10}
                            height={28}
                            padding={{ left: 8, right: 8 }}
                            tickFormatter={(value) => {
                                if (value === null || value === undefined) {
                                    return '';
                                }
                                const date = new Date(value);
                                if (Number.isNaN(date.getTime())) {
                                    return String(value);
                                }
                                const day = String(date.getDate()).padStart(2, '0');
                                const month = String(date.getMonth() + 1).padStart(2, '0');
                                return `${day}/${month}`;
                            }}
                            interval="preserveStartEnd"
                            minTickGap={60}
                        />

                        <YAxis
                            hide={!showAxes}
                            orientation="right"
                            domain={chartDomain}
                            tick={{ fill: '#aeb9c9', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            tickLine={{ stroke: 'rgba(255,255,255,0.18)' }}
                            width={70}
                            tickFormatter={(value) => {
                                if (value === null || value === undefined || Number.isNaN(Number(value))) {
                                    return '';
                                }
                                const numberValue = Number(value);
                                const absValue = Math.abs(numberValue);
                                if (absValue < 0.01) {
                                    return numberValue.toFixed(5);
                                }
                                if (absValue < 0.1) {
                                    return numberValue.toFixed(4);
                                }
                                if (absValue < 1) {
                                    return numberValue.toFixed(3);
                                }
                                return numberValue.toLocaleString(undefined, {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                });
                            }}
                            tickCount={6}
                            label={
                                showAxes
                                    ? {
                                          value: 'Price (USD)',
                                          angle: -90,
                                          position: 'outside',
                                          fill: '#94a3b8',
                                          dx: 45,
                                      }
                                    : undefined
                            }
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
                            stroke={trendColor}
                            strokeWidth={2}
                            fill={`url(#sparkline-gradient-${chartId})`}
                            dot={false}
                            activeDot={{
                                r: 4,
                                fill: trendColor,
                                stroke: '#ffffff',
                                strokeWidth: 1,
                            }}
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            ) : (
                <div className="coin-sparkline-placeholder">
                    {placeholderText}
                </div>
            )}
        </div>
    );
}

export default SparklineChart;
