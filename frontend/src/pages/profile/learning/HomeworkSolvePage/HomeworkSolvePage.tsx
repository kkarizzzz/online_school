import { useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, ClipboardList, FileQuestion } from 'lucide-react';
import { useCallback, useEffect, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import { HOMEWORK_LIST_ROUTE, homeworkKeys, useHomeworkAttempt, useHomeworkList } from '../../../../entities/homework';
import { statsKeys } from '../../../../entities/stats';
import { cn, pluralize } from '../../../../shared/lib';
import { Button, Container } from '../../../../shared/ui';
import { AttemptSolver } from '../../../../widgets/attempt-solver';
import styles from './HomeworkSolvePage.module.css';


export const HomeworkSolvePage = (): JSX.Element => {
    const { homeworkId = '' } = useParams();
    const id = Number(homeworkId);
    const queryClient = useQueryClient();
    const { data: attempt, isPending, isError } = useHomeworkAttempt(id);
    const { data: list } = useHomeworkList();
    const homework = list?.items.find((h) => h.id === id);

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [homeworkId]);

    // Список ДЗ и статистика должны увидеть сохранённые ответы и сдачу
    useEffect(() => () => {
        void queryClient.invalidateQueries({ queryKey: homeworkKeys.all });
    }, [queryClient]);

    const onSubmitted = useCallback(() => {
        void queryClient.invalidateQueries({ queryKey: homeworkKeys.all });
        void queryClient.invalidateQueries({ queryKey: statsKeys.all });
    }, [queryClient]);

    if (isPending && Number.isInteger(id) && id > 0) {
        return (
            <Container variant='page'>
                <p className={styles.message}>Загружаем домашнее задание…</p>
            </Container>
        );
    }

    if (isError || !attempt) {
        return (
            <Container variant='page'>
                <div className={cn('glass', styles.missing)}>
                    <FileQuestion size={34} />
                    <p className={styles.missingTitle}>Домашнее задание не найдено</p>
                    <Button as={Link} to={HOMEWORK_LIST_ROUTE} variant="outline" size="m" radius={12}>
                        <ArrowLeft size={18} />К домашним заданиям
                    </Button>
                </div>
            </Container>
        );
    }

    const kicker = ['Домашнее задание', homework?.topic, pluralize(attempt.items.length, 'задание', 'задания', 'заданий')]
        .filter(Boolean)
        .join(' · ');

    return (
        <Container variant='page'>
            <AttemptSolver
                key={attempt.id}
                attempt={attempt}
                back={{ to: attempt.submittedAt ? `${HOMEWORK_LIST_ROUTE}?tab=done` : HOMEWORK_LIST_ROUTE, label: 'Домашние задания' }}
                kicker={kicker}
                onSubmitted={onSubmitted}
                resultActions={
                    <Button as={Link} to={`${HOMEWORK_LIST_ROUTE}?tab=done`} size="m" radius={12}>
                        <ClipboardList size={18} />К домашним заданиям
                    </Button>
                }
            />
        </Container>
    );
};
