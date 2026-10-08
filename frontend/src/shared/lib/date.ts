/** «2026-10-13» → «13 октября» */
export const formatDayMonth = (iso: string): string =>
    new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });

/** «2026-10-13» → «13 октября 2026» */
export const formatLongDate = (iso: string): string =>
    new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).replace(' г.', '');

/** 14100 секунд → «3 ч 55 мин» */
export const formatSpentTime = (seconds: number): string => {
    const m = Math.round(seconds / 60);
    const h = Math.floor(m / 60);
    if (!h) return `${m} мин`;
    return m % 60 ? `${h} ч ${m % 60} мин` : `${h} ч`;
};

/** 75 → «1:15», 3725 → «1:02:05» */
export const formatClock = (seconds: number): string => {
    const s = Math.max(0, Math.floor(seconds));
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    const mm = h ? String(m).padStart(2, '0') : String(m);
    return `${h ? `${h}:` : ''}${mm}:${String(sec).padStart(2, '0')}`;
};
