import 'katex/dist/katex.min.css';
import type { JSX } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { cn } from '../../lib';
import styles from './Markdown.module.css';
import type { MarkdownProps } from './Markdown.props';


export const Markdown = ({ source, className, ...props }: MarkdownProps): JSX.Element => {
    return (
        <div className={cn(styles.md, className)} {...props}>
            <ReactMarkdown
                remarkPlugins={[remarkMath, remarkGfm]}
                rehypePlugins={[rehypeKatex]}
            >
                {source}
            </ReactMarkdown>
        </div>
    );
};
