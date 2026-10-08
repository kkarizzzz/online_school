export type NotificationType =
    | 'homework_assigned'
    | 'homework_due_soon'
    | 'homework_overdue'
    | 'homework_submitted'
    | 'attempt_graded'
    | 'achievement_unlocked'
    | 'system';

export interface AppNotification {
    id: number;
    type: NotificationType;
    title: string;
    body: string | null;
    /** Ссылочные данные: student_assignment_id, attempt_id, deadline_at… */
    payload: Record<string, unknown>;
    createdAt: string;
    readAt: string | null;
}

export interface NotificationPage {
    items: AppNotification[];
    unreadCount: number;
}
