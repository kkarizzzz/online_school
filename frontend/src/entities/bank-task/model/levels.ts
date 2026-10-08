import type { Difficulty } from '../../exam-task';
import type { BankLevel } from './types';

/** Подпись и ранг сложности (ранг — для сортировки и шкалы из четырёх делений) */
export const BANK_LEVELS: Record<BankLevel, { label: string; rank: number }> = {
    base: { label: 'Базовый', rank: 1 },
    medium: { label: 'Средний', rank: 2 },
    hard: { label: 'Сложный', rank: 3 },
    coffin: { label: 'Гроб', rank: 4 },
};

const BY_DIFFICULTY: Record<Difficulty, BankLevel> = { 1: 'base', 2: 'medium', 3: 'hard', 4: 'coffin' };

/** Сложность с сервера (1–4) → уровень для шкалы */
export const levelOf = (difficulty: Difficulty): BankLevel => BY_DIFFICULTY[difficulty];

export const BANK_PART_LABEL: Record<1 | 2, string> = {
    1: 'Часть 1 · краткий ответ',
    2: 'Часть 2 · развёрнутый ответ',
};
