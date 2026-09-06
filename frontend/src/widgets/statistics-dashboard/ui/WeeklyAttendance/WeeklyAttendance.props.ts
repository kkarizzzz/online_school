import type { DetailedHTMLProps, HTMLAttributes } from "react";
import type { ChartDataPoint } from "../../../../shared/ui/LineChart/LineChart.props";

export interface WeeklyAttendanceProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    data?: ChartDataPoint[];
}