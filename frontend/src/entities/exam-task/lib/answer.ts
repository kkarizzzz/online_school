import type { AnswerType, Difficulty } from '../model/types';

export const isBlankAnswer = (input: string | undefined | null): boolean => String(input ?? '').trim() === '';

export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
    1: 'Базовый',
    2: 'Средний',
    3: 'Сложный',
    4: 'Гроб',
};

/** Подсказка в пустом поле ответа */
export const ANSWER_PLACEHOLDERS: Record<AnswerType, string> = {
    short: 'Введите ответ',
    digits_set: 'Например, 135',
    sequence: 'Числа через пробел',
    detailed: 'Кратко запишите решение и ответ',
};

/** Как записывать ответ */
export const ANSWER_HINTS: Record<AnswerType, string> = {
    short: 'Десятичную дробь можно писать через запятую или точку.',
    digits_set: 'Номера ответов без пробелов, в любом порядке.',
    sequence: 'Несколько чисел через пробел, в указанном порядке.',
    detailed: 'Решение проверит преподаватель по критериям ЕГЭ. Можно приложить фото решения.',
};
