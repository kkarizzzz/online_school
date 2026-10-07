import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export interface MathTextProps extends Omit<DetailedHTMLProps<HTMLAttributes<HTMLSpanElement>, HTMLSpanElement>, 'children'> {
    /** Текст с формулами LaTeX в $...$ */
    text: string;
}
