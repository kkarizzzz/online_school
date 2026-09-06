import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export type ChartDataPoint = {
    day: string;
    value: number;
};

export interface LineChartProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    data: ChartDataPoint[];
}