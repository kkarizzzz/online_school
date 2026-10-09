import type { Difficulty, PracticeNumber } from '../../../entities/practice-task';
import { plural } from '../../../shared/lib';

export const PRACTICE_ROUTE = '/profile/learning/practice';
export const PERSONAL_ROUTE = `${PRACTICE_ROUTE}/personal`;

export const ALL_DIFFICULTIES: Difficulty[] = [1, 2, 3, 4];

/**
 * Откуда лента берёт задания.
 * tornado — все темы первой части; personal — персональная подборка;
 * custom — подборка, суженная прямо в ленте (номер или часть его подтем).
 */
export interface PracticeScope {
    kind: 'tornado' | 'personal' | 'custom';
    /** Темы; у «Торнадо» пусто — берутся все темы первой части */
    topicIds: number[];
    /** Сложности; пусто — все */
    difficulties: Difficulty[];
}

export const TORNADO: PracticeScope = { kind: 'tornado', topicIds: [], difficulties: [] };

/** Выбраны все сложности — фильтровать не нужно */
export const isAllDifficulties = (d: Difficulty[]): boolean => !d.length || ALL_DIFFICULTIES.every((x) => d.includes(x));

/** Фильтр по сложности для API: все выбраны — пустой список */
export const difficultyFilter = (d: Difficulty[]): Difficulty[] => (isAllDifficulties(d) ? [] : [...d].sort());

// ----------------------------------- адрес страницы -----------------------------------

const ids = (value: string | null): number[] => (value ?? '').split(',').map(Number).filter(Boolean);

/** ?mode=tornado, ?mode=personal или ?topics=1,2&levels=2,3 */
export const scopeFromParams = (params: URLSearchParams, personal: PracticeScope): PracticeScope | null => {
    const mode = params.get('mode');
    if (mode === 'tornado') return TORNADO;
    if (mode === 'personal') return personal.topicIds.length ? personal : null;
    const topicIds = ids(params.get('topics'));
    if (!topicIds.length) return null;
    return { kind: 'custom', topicIds, difficulties: ids(params.get('levels')) as Difficulty[] };
};

export const scopeToParams = (scope: PracticeScope): Record<string, string> => {
    if (scope.kind !== 'custom') return { mode: scope.kind };
    const params: Record<string, string> = { topics: scope.topicIds.join(',') };
    const levels = difficultyFilter(scope.difficulties);
    if (levels.length) params.levels = levels.join(',');
    return params;
};

// ----------------------------------- подписи -----------------------------------

/** Номер, к которому относится тема */
export const numberOfTopic = (numbers: PracticeNumber[], topicId: number): PracticeNumber | undefined =>
    numbers.find((n) => n.topics.some((t) => t.id === topicId));

/** Номера, в которых есть темы подборки, по порядку */
export const numbersOfTopics = (numbers: PracticeNumber[], topicIds: number[]): PracticeNumber[] =>
    numbers.filter((n) => n.topics.some((t) => topicIds.includes(t.id)));

/** Сколько заданий в темах с учётом сложности и сколько из них решено */
export const countTasks = (
    numbers: PracticeNumber[],
    topicIds: number[] | null,
    difficulties: Difficulty[],
    part: number | null = null,
): { total: number; solved: number } => {
    const all = isAllDifficulties(difficulties);
    let total = 0;
    let solved = 0;
    for (const n of numbers) {
        if (part !== null && n.part !== part) continue;
        for (const t of n.topics) {
            if (topicIds && !topicIds.includes(t.id)) continue;
            for (const l of t.levels) {
                if (!all && !difficulties.includes(l.difficulty)) continue;
                total += l.taskCount;
                solved += l.solvedCount;
            }
        }
    }
    return { total, solved };
};

/** «№1 целиком · №6: 2 подтемы» */
export const describeTopics = (numbers: PracticeNumber[], topicIds: number[]): string =>
    numbersOfTopics(numbers, topicIds).map((n) => {
        const picked = n.topics.filter((t) => topicIds.includes(t.id)).length;
        return picked === n.topics.length
            ? `№${n.number} целиком`
            : `№${n.number}: ${picked} ${plural(picked, 'подтема', 'подтемы', 'подтем')}`;
    }).join(' · ');

const DIFFICULTY_NAMES: Record<Difficulty, string> = { 1: 'базовый', 2: 'средний', 3: 'сложный', 4: 'гроб' };

/** «средний, сложный»; все сложности — пустая строка */
export const describeDifficulties = (d: Difficulty[]): string =>
    isAllDifficulties(d) ? '' : [...d].sort().map((x) => DIFFICULTY_NAMES[x]).join(', ');

/** Заголовок ленты: строка над названием и само название */
export const scopeTitle = (scope: PracticeScope, numbers: PracticeNumber[]): { label: string; title: string } => {
    if (scope.kind === 'tornado') return { label: 'Номера первой части вперемешку', title: 'Торнадо' };
    const levels = describeDifficulties(scope.difficulties);
    if (scope.kind === 'personal') {
        return { label: levels ? `Ваша подборка · сложность: ${levels}` : 'Ваша подборка номеров и подтем', title: 'Персональный' };
    }

    const inScope = numbersOfTopics(numbers, scope.topicIds);
    const suffix = levels ? ` · сложность: ${levels}` : '';
    if (inScope.length !== 1) {
        return { label: `Подборка${suffix}`, title: `Номера ${inScope.map((n) => n.number).join(', ')}` };
    }
    const [n] = inScope;
    const picked = n.topics.filter((t) => scope.topicIds.includes(t.id));
    if (picked.length === n.topics.length) return { label: `Задание №${n.number}${suffix}`, title: n.title ?? `№${n.number}` };
    return {
        label: `№${n.number} · ${n.title ?? ''}${suffix}`,
        title: picked.length === 1 ? picked[0].name : `${picked.length} ${plural(picked.length, 'подтема', 'подтемы', 'подтем')}`,
    };
};
