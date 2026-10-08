/** Генератор случайных чисел [0, 1) */
export type Rng = () => number;

/**
 * Генератор по зерну-строке (mulberry32): одно и то же зерно всегда даёт одну и ту же
 * последовательность — так mock-задания одинаковые при каждой загрузке.
 */
export const seededRng = (seed: string): Rng => {
    let h = 1779033703 ^ seed.length;
    for (let i = 0; i < seed.length; i++) {
        h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
        h = (h << 13) | (h >>> 19);
    }
    let a = h >>> 0;
    return () => {
        a = (a + 0x6D2B79F5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
};

/** Целое из [min, max] */
export const rngInt = (r: Rng, min: number, max: number): number => min + Math.floor(r() * (max - min + 1));

export const rngPick = <T>(r: Rng, items: readonly T[]): T => items[Math.floor(r() * items.length)];
