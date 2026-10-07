import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export interface ProgressRingProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    value?: number;
    label?: string;
    size?: number;
    stroke?: number;
    tone?: 'primary' | 'done';
    /** Маленькое кольцо: процент мельче, без подписи и свечения */
    compact?: boolean;
}
