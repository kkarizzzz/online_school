import type { JSX } from 'react';
import styles from './Highlight.module.css';

interface HighlightProps {
    text: string;
    query: string;
}

const escapeRegExp = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** Подсвечивает совпадения с поиском */
export const Highlight = ({ text, query }: HighlightProps): JSX.Element => {
    if (!query) return <>{text}</>;
    const parts = text.split(new RegExp(`(${escapeRegExp(query)})`, 'gi'));
    return (
        <>
            {parts.map((part, i) => (i % 2 ? <mark key={i} className={styles.mark}>{part}</mark> : part))}
        </>
    );
};
