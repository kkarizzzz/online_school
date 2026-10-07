/** Доля в процентах, округлённая до целого; при total = 0 — 0 */
export const percent = (part: number, total: number): number =>
    total ? Math.round((part / total) * 100) : 0;

/** Секунды → «m:ss» */
export const formatDuration = (seconds: number): string =>
    `${Math.floor(seconds / 60)}:${String(Math.round(seconds % 60)).padStart(2, '0')}`;

export const randInt = (min: number, max: number): number =>
    min + Math.floor(Math.random() * (max - min + 1));

/** Перемешанная копия массива (Фишер — Йетс) */
export const shuffle = <T>(items: readonly T[]): T[] => {
    const result = [...items];
    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
};

/** Буквы вариантов ответа: А, Б, В… */
export const OPTION_LETTERS = 'АБВГДЕЖЗ';
