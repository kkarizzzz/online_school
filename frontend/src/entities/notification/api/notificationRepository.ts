import { API, apiClient } from '../../../shared/api';
import type { AppNotification, NotificationPage, NotificationType } from '../model/types';

interface NotificationDto {
    id: number;
    type: NotificationType;
    title: string;
    body: string | null;
    payload: Record<string, unknown>;
    created_at: string;
    read_at: string | null;
}

const toNotification = (n: NotificationDto): AppNotification => ({
    id: n.id,
    type: n.type,
    title: n.title,
    body: n.body,
    payload: n.payload,
    createdAt: n.created_at,
    readAt: n.read_at,
});

export const notificationRepository = {
    async getLatest(limit = 20): Promise<NotificationPage> {
        const { data } = await apiClient.get<{ items: NotificationDto[]; unread_count: number }>(
            API.notifications.list, { params: { limit } },
        );
        return { items: data.items.map(toNotification), unreadCount: data.unread_count };
    },

    async getUnreadCount(): Promise<number> {
        const { data } = await apiClient.get<{ unread_count: number }>(API.notifications.unread);
        return data.unread_count;
    },

    /** ids не передан — прочитать все */
    async markRead(ids?: number[]): Promise<void> {
        await apiClient.post(API.notifications.read, { ids: ids ?? null });
    },
};
