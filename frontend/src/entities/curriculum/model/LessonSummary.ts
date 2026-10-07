import type { Lesson } from './Lesson';
import type { LessonSummaryData, OutlineNodeDto } from './types';

const capitalize = (s: string): string => s.charAt(0).toUpperCase() + s.slice(1);
const flatText = (n: OutlineNodeDto): string => n.t + (n.c ? `: ${n.c.map(flatText).join('; ')}` : '');

const FORMULA_LINE = /^([^:]{2,60}):\s(.+)$/;
const FORMULA_SIGNS = /[=<>≤≥√^·≠⋮≡]/;

/** Мини-конспект урока: написанный вручную или собранный из плана */
export class LessonSummary {
    /**
     * Конспект без ручного текста: «Подпись: формула» → карточка формулы, остальное → «Главное».
     */
    static fromOutline(lesson: Lesson): LessonSummaryData {
        const formulas: [string, string][] = [];
        const points: string[] = [];
        lesson.outline.forEach((n) => {
            const m = n.t.match(FORMULA_LINE);
            if (!n.c && m && FORMULA_SIGNS.test(m[2])) formulas.push([m[1], m[2]]);
            else points.push(flatText(n));
        });
        const intro = lesson.note ? `${capitalize(lesson.note)}.` : `Урок из темы «${lesson.topic.name}».`;
        return { intro, formulas, points };
    }

    static resolve(lesson: Lesson, manual: LessonSummaryData | null | undefined): LessonSummaryData {
        return manual ?? LessonSummary.fromOutline(lesson);
    }
}
