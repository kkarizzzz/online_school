import type { JSX } from 'react';
import type { HtmlTextProps } from './HtmlText.props';

/**
 * Короткий текст с простой разметкой (индексы логарифмов, степени).
 * Только для контента курса — пользовательский ввод сюда не попадает.
 */
export const HtmlText = ({ html, ...props }: HtmlTextProps): JSX.Element => (
    <span dangerouslySetInnerHTML={{ __html: html }} {...props} />
);
