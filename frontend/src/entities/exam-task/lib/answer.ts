/** Ответ в виде, как его пишут на ЕГЭ: 0.25 → «0,25» */
export const formatAnswer = (answer: number): string => String(answer).replace('.', ',');

export const isBlankAnswer = (input: string | undefined | null): boolean => String(input ?? '').trim() === '';

/** Ответ ученика совпадает с верным: «0,25» = «0.25» = «.25» */
export const isCorrectAnswer = (input: string | undefined | null, answer: number): boolean => {
    if (isBlankAnswer(input)) return false;
    const x = Number(String(input).trim().replace(',', '.').replace(/\s/g, ''));
    return Number.isFinite(x) && Math.abs(x - answer) < 1e-6;
};
