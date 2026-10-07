import type { DetailedHTMLProps, HTMLAttributes } from "react";

export interface ProgressBarProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    value: number;
    max?: number;
    /** Цвет заливки: primary, зелёный «пройдено» или произвольный CSS-цвет */
    tone?: 'primary' | 'done' | (string & {});
    size?: 's' | 'm';
}
