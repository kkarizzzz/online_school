import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { notificationRepository } from '../api/notificationRepository';

export const notificationKeys = {
    all: ['notifications'] as const,
    unread: ['notifications', 'unread'] as const,
    latest: ['notifications', 'latest'] as const,
};

/** Как часто проверять новые уведомления, мс */
const POLL_INTERVAL = 60_000;

/** Число на колокольчике — обновляется раз в минуту и при возвращении на вкладку */
export const useUnreadCount = (enabled = true) =>
    useQuery({
        queryKey: notificationKeys.unread,
        queryFn: () => notificationRepository.getUnreadCount(),
        refetchInterval: POLL_INTERVAL,
        enabled,
    });

export const useLatestNotifications = (enabled: boolean) =>
    useQuery({
        queryKey: notificationKeys.latest,
        queryFn: () => notificationRepository.getLatest(),
        enabled,
    });

export const useMarkRead = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (ids?: number[]) => notificationRepository.markRead(ids),
        onSettled: () => queryClient.invalidateQueries({ queryKey: notificationKeys.all }),
    });
};
