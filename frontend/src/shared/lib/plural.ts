/** Русское склонение по числу: plural(5, 'урок', 'урока', 'уроков') → 'уроков' */
export const plural = (n: number, one: string, few: string, many: string): string => {
    const m10 = n % 10;
    const m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
};

/** «5 уроков» */
export const pluralize = (n: number, one: string, few: string, many: string): string =>
    `${n} ${plural(n, one, few, many)}`;
