import { AxisBottom } from '@visx/axis';
import { curveMonotoneX } from '@visx/curve';
import { Group } from '@visx/group';
import { ParentSize } from '@visx/responsive';
import { scaleLinear, scalePoint } from '@visx/scale';
import { AreaClosed, Circle, LinePath } from '@visx/shape';
import { TooltipWithBounds, useTooltip } from '@visx/tooltip';
import { useMemo, type JSX } from 'react';
import { cn } from '../../lib';
import styles from './LineChart.module.css';
import type { ChartDataPoint, LineChartProps } from './LineChart.props';

const getX = (d: ChartDataPoint) => d.day;
const getY = (d: ChartDataPoint) => d.value;

const ChartInner = ({ width, height, data }: { width: number; height: number; data: ChartDataPoint[] }) => {
    const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<ChartDataPoint>();

    const margin = { top: 20, right: 20, bottom: 40, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = useMemo(() => scalePoint<string>({
        range: [0, innerWidth],
        domain: data.map(getX),
        padding: 0,
    }), [innerWidth, data]);

    const yScale = useMemo(() => scaleLinear<number>({
        range: [innerHeight, 0],
        domain: [0, Math.max(...data.map(getY)) * 1.2], 
    }), [innerHeight, data]);

    if (width < 10) return null;

    return (
        <div className={styles.chartContainer}>
            <svg width={width} height={height}>
                <defs>
                    <linearGradient id="area-gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.25} />
                        <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                    </linearGradient>
                </defs>

                <Group left={margin.left} top={margin.top}>
                    <AxisBottom
                        top={innerHeight}
                        scale={xScale}
                        stroke="transparent"
                        tickStroke="transparent"
                        tickLabelProps={() => ({
                            fill: 'var(--text-secondary)',
                            fontSize: 12,
                            textAnchor: 'middle',
                            dy: 10,
                            fontFamily: 'var(--font-sans)',
                        })}
                    />

                    <AreaClosed<ChartDataPoint>
                        data={data}
                        x={d => xScale(getX(d)) ?? 0}
                        y={d => yScale(getY(d)) ?? 0}
                        yScale={yScale}
                        fill="url(#area-gradient)"
                        curve={curveMonotoneX}
                    />

                    <LinePath<ChartDataPoint>
                        data={data}
                        x={d => xScale(getX(d)) ?? 0}
                        y={d => yScale(getY(d)) ?? 0}
                        stroke="var(--primary)"
                        strokeWidth={3}
                        curve={curveMonotoneX}
                    />

                    {data.map((d, i) => {
                        const cx = xScale(getX(d)) ?? 0;
                        const cy = yScale(getY(d)) ?? 0;
                        const bandWidth = innerWidth / (data.length - 1);
                        const isHovered = tooltipData === d;

                        return (
                            <g key={`point-${i}`}>
                                <Circle
                                    cx={cx}
                                    cy={cy}
                                    r={isHovered ? 6 : 3.5}
                                    fill="var(--bg-primary)"
                                    stroke="var(--primary)"
                                    strokeWidth={isHovered ? 3 : 2}
                                    className={styles.point}
                                />

                                {isHovered && (
                                    <Circle cx={cx} cy={cy} r={12} fill="var(--primary)" opacity={0.15} className={styles.point} />
                                )}
                                
                                <rect
                                    x={cx - bandWidth / 2}
                                    y={0}
                                    width={bandWidth}
                                    height={innerHeight}
                                    fill="transparent"
                                    onMouseEnter={() => showTooltip({
                                        tooltipData: d,
                                        tooltipLeft: cx + margin.left,
                                        tooltipTop: cy + margin.top,
                                    })}
                                    onMouseLeave={hideTooltip}
                                />
                            </g>
                        );
                    })}
                </Group>
            </svg>

            {tooltipData && (
                <TooltipWithBounds
                    top={tooltipTop}
                    left={tooltipLeft}
                    className={cn('glass', styles.tooltip)}
                    style={{ position: 'absolute', pointerEvents: 'none' }}
                >
                    <div className={styles.tooltipValue}>
                        {tooltipData.value} <span className={styles.tooltipUnit}>ч</span>
                    </div>
                </TooltipWithBounds>
            )}
        </div>
    );
};

export const LineChart = ({ data, className, ...props }: LineChartProps): JSX.Element => {
    return (
        <div className={cn(styles.wrapper, className)} {...props}>
            <ParentSize>
                {({ width, height }) => <ChartInner width={width} height={height} data={data} />}
            </ParentSize>
        </div>
    );
};