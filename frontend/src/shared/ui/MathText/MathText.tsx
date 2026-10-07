import katex from 'katex';
import 'katex/dist/katex.min.css';
import { useMemo, type JSX } from 'react';
import type { MathTextProps } from './MathText.props';

const escapeHtml = (s: string): string =>
    s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string));

/** Строка с формулами в $...$ → HTML: текст экранируется, формулы рендерит KaTeX */
const renderInlineMath = (src: string): string =>
    src
        .split(/(\$[^$]+\$)/g)
        .map((part) => (part.length > 2 && part.startsWith('$') && part.endsWith('$')
            ? katex.renderToString(part.slice(1, -1), { throwOnError: false })
            : escapeHtml(part)))
        .join('');


export const MathText = ({ text, ...props }: MathTextProps): JSX.Element => {
    const html = useMemo(() => renderInlineMath(text), [text]);

    return <span dangerouslySetInnerHTML={{ __html: html }} {...props} />;
};
