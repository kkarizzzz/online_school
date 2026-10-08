import { Check, LifeBuoy } from 'lucide-react';
import { useState, type FormEvent, type JSX } from 'react';
import { useUpdateUser, useUser, type User } from '../../../../entities/user';
import { cn, formatPhone, parseApiError } from '../../../../shared/lib';
import { Button, Card, Divider, Input } from '../../../../shared/ui';
import styles from './ProfileData.module.css';
import type { ProfileDataProps } from './ProfileData.props';


export const ProfileData = ({ className, ...props }: ProfileDataProps): JSX.Element => {
    const { data: user } = useUser();
    // Сохранение живёт здесь: после него форма пересоздаётся, а «Сохранено» должно остаться
    const mutation = useUpdateUser();

    return (
        <Card variant='glass' className={className} {...props}>
            {/* Форма пересоздаётся, когда имя пришло с сервера или сохранилось */}
            {user && <ProfileForm key={`${user.id}:${user.firstName}:${user.lastName ?? ''}`} user={user} mutation={mutation} />}
        </Card>
    );
};


interface ProfileFormProps {
    user: User;
    mutation: ReturnType<typeof useUpdateUser>;
}

const ProfileForm = ({ user, mutation }: ProfileFormProps): JSX.Element => {
    const { mutate: save, isPending, isSuccess, error, reset } = mutation;
    const [firstName, setFirstName] = useState(user.firstName);
    const [lastName, setLastName] = useState(user.lastName ?? '');

    const changed = firstName.trim() !== user.firstName || lastName.trim() !== (user.lastName ?? '');

    const submit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!firstName.trim() || !changed) return;
        save({ firstName: firstName.trim(), lastName: lastName.trim() || null });
    };

    const edit = (setter: (v: string) => void) => (value: string) => {
        setter(value);
        if (isSuccess || error) reset();
    };

    return (
        <form onSubmit={submit} noValidate>
            <div className={styles.formGrid}>
                <label className={styles.field}>
                    <span className={styles.label}>Имя</span>
                    <Input
                        value={firstName}
                        onChange={(e) => edit(setFirstName)(e.target.value)}
                        placeholder="Введите имя"
                        className={styles.input}
                        maxLength={100}
                    />
                </label>

                <label className={styles.field}>
                    <span className={styles.label}>Фамилия</span>
                    <Input
                        value={lastName}
                        onChange={(e) => edit(setLastName)(e.target.value)}
                        placeholder="Необязательно"
                        className={styles.input}
                        maxLength={100}
                    />
                </label>

                <label className={styles.field}>
                    <span className={styles.label}>Телефон</span>
                    <Input
                        type="tel"
                        value={formatPhone(user.phoneNumber)}
                        readOnly
                        placeholder="+7 (___) ___-__-__"
                        title="Номер телефона нельзя изменить самостоятельно"
                        className={cn(styles.input, styles.numberInput)}
                    />
                </label>
            </div>

            {error && <p className={styles.error}>{parseApiError(error, 'Не удалось сохранить')}</p>}

            <Divider />

            <div className={styles.actionRow}>
                <Button type="submit" size="s" radius={18} isLoading={isPending} disabled={!changed || !firstName.trim()}>
                    {isSuccess && !changed ? <><Check size={16} />Сохранено</> : 'Сохранить изменения'}
                </Button>
                <Button type="button" size="s" variant="ghost-secondary" radius={18}>
                    <LifeBuoy size={18} />
                    Написать в поддержку
                </Button>
            </div>
        </form>
    );
};
