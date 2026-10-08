import { pluralize } from '../../../shared/lib';
import type { AttemptBrief, AttemptData } from '../model/types';

/** Короткий итог сданной попытки: «74 балла», «8 из 10 баллов», «на проверке» */
export const scoreLabel = (a: AttemptBrief | AttemptData): string => {
    if (a.status === 'checking') return 'на проверке';
    if (a.secondaryScore !== null) return pluralize(a.secondaryScore, 'балл', 'балла', 'баллов');
    return `${a.primaryScore ?? 0} из ${pluralize(a.maxScore ?? 0, 'балла', 'баллов', 'баллов')}`;
};
