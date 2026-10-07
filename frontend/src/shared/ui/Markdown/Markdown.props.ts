import type { DetailedHTMLProps, HTMLAttributes } from 'react';

export interface MarkdownProps extends Omit<DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>, 'children'> {
    /** Markdown + LaTeX ($...$ и $$...$$) */
    source: string;
}
