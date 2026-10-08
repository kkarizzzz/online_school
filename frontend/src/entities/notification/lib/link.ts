import type { AppNotification } from '../model/types';

const LEARNING = '/profile/learning';

const num = (v: unknown): number | null => (typeof v === 'number' && Number.isInteger(v) ? v : null);

/** Куда ведёт уведомление; null — никуда */
export const notificationLink = (n: AppNotification): string | null => {
    const homework = num(n.payload.student_assignment_id);
    const attempt = num(n.payload.attempt_id);
    switch (n.type) {
        case 'homework_assigned':
        case 'homework_due_soon':
        case 'homework_overdue':
            return homework ? `${LEARNING}/homework/${homework}` : `${LEARNING}/homework`;
        case 'attempt_graded':
            if (homework) return `${LEARNING}/homework/${homework}`;
            return attempt ? `${LEARNING}/variants/attempts/${attempt}` : null;
        case 'achievement_unlocked':
            return '/profile/statistics';
        default:
            return null;
    }
};
