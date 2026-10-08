import type { JSX } from 'react';
import { Link } from 'react-router';
import { useUser } from '../../../../entities/user';
import { NotificationBtn } from '../../../../features/notifications';
import { ThemeToggleBtn } from '../../../../features/theme-switcher';
import { cn } from '../../../../shared/lib';
import { Avatar, Button } from '../../../../shared/ui';
import styles from './UserActions.module.css';
import type { UserActionsProps } from './UserActions.props';

const ROLE_LABELS: Record<string, string> = {
    student: 'Ученик',
    parent: 'Родитель',
    teacher: 'Преподаватель',
    admin: 'Администратор',
};

export const UserActions = ({ className, ...props }: UserActionsProps): JSX.Element => {
    const { data: user } = useUser();

    return (
        <div className={cn(styles.actionsGroup, className)} {...props}>
            <ThemeToggleBtn />
            <NotificationBtn />

            <Button 
                as={Link}
                to='/profile'
                variant="ghost-secondary" 
                className={styles.profileBtn}
                radius={20}
                aria-label="Профиль пользователя"
            >
                <Avatar 
                    firstName={user?.firstName} 
                    lastName={user?.lastName} 
                    size={36} 
                    className={styles.avatar}
                />

                <span className={styles.userInfo}>
                    <span className={styles.userName}>{user?.firstName}</span>
                    <span className={styles.userRole}>{user && ROLE_LABELS[user.role]}</span>
                </span>
            </Button>
        </div>
    );
};