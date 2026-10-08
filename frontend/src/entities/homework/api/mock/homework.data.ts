import type { ExamTaskNumber } from '../../../exam-task';
import type { HomeworkDto } from '../../model/types';

/**
 * ДЗ от преподавателя (заглушка, перенесено из concepts/homework_page/static/homework.js).
 * answered — сколько задач уже решено в начатом ДЗ: первые answered задач подставляются с верными ответами,
 * пока своей сессии нет. result — сданное ДЗ: points — 1 верно / 0 неверно по задачам.
 */
export interface HomeworkMock extends Omit<HomeworkDto, 'session' | 'result' | 'numbers'> {
    numbers: ExamTaskNumber[];
    answered?: number;
    result?: { points: string; minutes: number; date: string };
}

export const HOMEWORK_MOCK: HomeworkMock[] = [
    // Тестовое: короткое ДЗ — быстро пройти путь до результатов
    { id: 'hw-test', title: 'Тестовое ДЗ: 3 задачи', topic: 'Разное', numbers: [1, 4, 6], tasks: 3, deadline: '2026-10-20', status: 'current' },
    { id: 'hw-derivative', title: 'Производная сложной функции', topic: 'Начала анализа', numbers: [8, 12], tasks: 8, deadline: '2026-10-13', status: 'current' },
    { id: 'hw-trig', title: 'Тригонометрические уравнения', topic: 'Тригонометрия', numbers: [13], tasks: 10, deadline: '2026-10-15', status: 'current', answered: 3 },
    { id: 'hw-stereo', title: 'Стереометрия: сечения', topic: 'Геометрия', numbers: [3, 14], tasks: 6, deadline: '2026-10-18', status: 'current' },
    { id: 'hw-ineq', title: 'Неравенства: метод интервалов', topic: 'Алгебра', numbers: [15], tasks: 9, deadline: '2026-10-08', status: 'current', result: { points: '111101111', minutes: 47, date: '2026-10-07' } },
    { id: 'hw-circle', title: 'Планиметрия: углы окружности', topic: 'Геометрия', numbers: [1, 17], tasks: 7, deadline: '2026-10-05', status: 'overdue', answered: 2 },
];
