export const BANK_ROUTE = '/profile/learning/task-bank';

/** Задания номера; topics — выбранные темы (не передаются, если выбраны все) */
export const bankNumberRoute = (n: number, topics?: string[]): string =>
    `${BANK_ROUTE}/${n}${topics?.length ? `?topics=${topics.map(encodeURIComponent).join(',')}` : ''}`;
