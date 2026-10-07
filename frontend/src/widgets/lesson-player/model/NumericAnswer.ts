/** Числовой ответ ученика: «2», «-2», «1,5», «3/2» */
export class NumericAnswer {
    private static readonly EPS = 1e-9;

    /** Число или null, если строка — не число */
    static parse(raw: string): number | null {
        const s = raw.trim().replace(/\s+/g, '').replace(/,/g, '.').replace(/[−–]/g, '-');
        if (!s) return null;
        const frac = s.match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);
        if (frac) return Number(frac[2]) === 0 ? null : Number(frac[1]) / Number(frac[2]);
        return /^-?\d+(?:\.\d+)?$/.test(s) ? Number(s) : null;
    }

    static matches(raw: string, accepted: string[]): boolean {
        const value = NumericAnswer.parse(raw);
        return value !== null && accepted.some((a) => {
            const expected = NumericAnswer.parse(a);
            return expected !== null && Math.abs(expected - value) < NumericAnswer.EPS;
        });
    }
}
