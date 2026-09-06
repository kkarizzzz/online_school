import type { DetailedHTMLProps, HTMLAttributes } from "react";

export interface ProgressBarProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    value: number;
    max?: number;
}