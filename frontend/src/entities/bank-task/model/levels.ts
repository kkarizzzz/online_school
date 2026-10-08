import type { BankLevel } from './types';

/** Подпись и ранг сложности (ранг — для сортировки и шкалы из четырёх делений) */
export const BANK_LEVELS: Record<BankLevel, { label: string; rank: number }> = {
    base: { label: 'Базовый', rank: 1 },
    medium: { label: 'Средний', rank: 2 },
    hard: { label: 'Сложный', rank: 3 },
    coffin: { label: 'Гроб', rank: 4 },
};

export const BANK_PART_LABEL: Record<1 | 2, string> = {
    1: 'Часть 1 · краткий ответ',
    2: 'Часть 2 · развёрнутый ответ',
};
