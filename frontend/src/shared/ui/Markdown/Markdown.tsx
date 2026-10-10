import 'katex/dist/katex.min.css';
import type { ComponentProps, JSX } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { cn } from '../../lib';
import styles from './Markdown.module.css';
import type { MarkdownProps } from './Markdown.props';


/** Картинка «…@2x.png» нарисована вдвое крупнее: показываем в половинном размере, но с полной чёткостью */
const Image = ({ node: _node, src, ...props }: ComponentProps<'img'> & { node?: unknown }): JSX.Element => {
    const retina = typeof src === 'string' && /@2x\.\w+$/.test(src);
    return <img src={src} srcSet={retina ? `${src} 2x` : undefined} loading="lazy" {...props} />;
};

export const Markdown = ({ source, className, ...props }: MarkdownProps): JSX.Element => {
    return (
        <div className={cn(styles.md, className)} {...props}>
            <ReactMarkdown
                remarkPlugins={[remarkMath, remarkGfm]}
                rehypePlugins={[rehypeKatex]}
                components={{ img: Image }}
            >
                {source}
            </ReactMarkdown>
        </div>
    );
};
