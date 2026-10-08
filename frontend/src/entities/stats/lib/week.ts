import type { DayActivity } from '../model/types';

const WEEKDAYS = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

/** «2026-10-08» → «Чт». Дата без времени — день недели считаем без сдвига часового пояса */
export const weekdayOf = (day: string): string => {
    const [y, m, d] = day.split('-').map(Number);
    return WEEKDAYS[new Date(y, m - 1, d).getDay()];
};

/** Сумма за неделю по полю: weekTotal(week, 'answered') */
export const weekTotal = (week: DayActivity[], key: 'answered' | 'correct' | 'seconds' | 'lessonsDone'): number =>
    week.reduce((sum, d) => sum + d[key], 0);

/** Часы с одним знаком после запятой: 5400 → 1.5 */
export const toHours = (seconds: number): number => Math.round(seconds / 360) / 10;
