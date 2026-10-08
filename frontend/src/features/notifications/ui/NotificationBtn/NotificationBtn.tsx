import { Bell, CheckCheck } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { useNavigate } from 'react-router';
import {
    notificationLink, useLatestNotifications, useMarkRead, useUnreadCount, type AppNotification,
} from '../../../../entities/notification';
import { cn, useClickOutside } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import styles from './NotificationBtn.module.css';
import type { NotificationBtnProps } from './NotificationBtn.props';

/** «5 мин назад», «вчера», «8 октября» */
const ago = (iso: string): string => {
    const minutes = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
    if (minutes < 1) return 'только что';
    if (minutes < 60) return `${minutes} мин назад`;
    const hours = Math.round(minutes / 60);
    if (hours < 24) return `${hours} ч назад`;
    if (hours < 48) return 'вчера';
    return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
};


/** Колокольчик: число непрочитанных и последние уведомления. Клик по уведомлению — прочитать и перейти */
export const NotificationBtn = ({ iconSize=40, className, ...props }: NotificationBtnProps): JSX.Element => {
    const [open, setOpen] = useState(false);
    const rootRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    const { data: unread = 0 } = useUnreadCount();
    const { data: page, isPending } = useLatestNotifications(open);
    const { mutate: markRead } = useMarkRead();
    const bellSize = iconSize * 0.6;

    useClickOutside({ ref: rootRef, handler: () => setOpen(false), enabled: open });

    useEffect(() => {
        if (!open) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setOpen(false);
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [open]);

    const openItem = (n: AppNotification) => {
        if (!n.readAt) markRead([n.id]);
        const to = notificationLink(n);
        setOpen(false);
        if (to) navigate(to);
    };

    return (
        <div className={styles.root} ref={rootRef}>
            <Button
                variant="ghost-accent"
                size="icon"
                iconSize={iconSize}
                className={cn(styles.bellBtn, className)}
                aria-label={unread ? `Уведомления: ${unread} новых` : 'Уведомления'}
                aria-expanded={open}
                aria-haspopup="dialog"
                onClick={() => setOpen((v) => !v)}
                {...props}
            >
                <Bell size={bellSize} strokeWidth={1.75} />
                {unread > 0 && <span className={styles.bellIndicator} />}
            </Button>

            {open && (
                <div className={cn('glass', styles.panel)} role="dialog" aria-label="Уведомления">
                    <div className={styles.head}>
                        <span className={styles.headTitle}>Уведомления</span>
                        {unread > 0 && (
                            <button type="button" className={styles.readAll} onClick={() => markRead(undefined)}>
                                <CheckCheck size={15} />Прочитать все
                            </button>
                        )}
                    </div>

                    {isPending ? (
                        <p className={styles.empty}>Загружаем…</p>
                    ) : !page?.items.length ? (
                        <p className={styles.empty}>Уведомлений пока нет</p>
                    ) : (
                        <ul className={styles.list}>
                            {page.items.map((n) => (
                                <li key={n.id}>
                                    <button
                                        type="button"
                                        className={cn(styles.item, { [styles.unread]: !n.readAt })}
                                        onClick={() => openItem(n)}
                                    >
                                        <span className={styles.itemTitle}>{n.title}</span>
                                        {n.body && <span className={styles.itemBody}>{n.body}</span>}
                                        <span className={styles.itemTime}>{ago(n.createdAt)}</span>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
};
