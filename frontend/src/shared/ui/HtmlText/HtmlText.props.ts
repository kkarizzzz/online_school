import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export interface HtmlTextProps extends Omit<DetailedHTMLProps<HTMLAttributes<HTMLSpanElement>, HTMLSpanElement>, 'children'> {
    /** Доверенная разметка из собственного контента курса: <sub>, <sup>, <b> */
    html: string;
}
