import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export interface ProgressRingProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    /** Заполнение кольца, 0–100 */
    value?: number;
    /** Текст в центре вместо «value%» — например, балл «74» */
    display?: string;
    label?: string;
    size?: number;
    stroke?: number;
    tone?: 'primary' | 'done';
    /** Маленькое кольцо: процент мельче, без подписи и свечения */
    compact?: boolean;
}
