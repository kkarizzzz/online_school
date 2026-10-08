import { useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, FileQuestion, FolderOpen, RotateCcw } from 'lucide-react';
import { useCallback, useEffect, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import type { AttemptData } from '../../../../entities/attempt';
import { statsKeys } from '../../../../entities/stats';
import {
    VARIANTS_ROUTE, useVariantAttempt, useVariantStart, variantKeys, variantSolveRoute,
} from '../../../../entities/variant';
import { cn, pluralize } from '../../../../shared/lib';
import { Button, Container } from '../../../../shared/ui';
import { AttemptSolver } from '../../../../widgets/attempt-solver';
import styles from './VariantSolvePage.module.css';

const kickerOf = (attempt: AttemptData): string =>
    [
        attempt.set.isStandard ? 'Вариант ЕГЭ' : 'Отработка',
        pluralize(attempt.items.length, 'задание', 'задания', 'заданий'),
        attempt.isRated ? null : 'повторная попытка',
    ].filter(Boolean).join(' · ');


const Missing = ({ text }: { text: string }): JSX.Element => (
    <Container variant='page'>
        <div className={cn('glass', styles.missing)}>
            <FileQuestion size={34} />
            <p className={styles.missingTitle}>{text}</p>
            <Button as={Link} to={VARIANTS_ROUTE} variant="outline" size="m" radius={12}>
                <ArrowLeft size={18} />В каталог вариантов
            </Button>
        </div>
    </Container>
);

const Loading = (): JSX.Element => (
    <Container variant='page'>
        <p className={styles.message}>Загружаем вариант…</p>
    </Container>
);

const useRefreshAfterSubmit = () => {
    const queryClient = useQueryClient();
    return useCallback(() => {
        void queryClient.invalidateQueries({ queryKey: variantKeys.list });
        void queryClient.invalidateQueries({ queryKey: statsKeys.all });
    }, [queryClient]);
};


/** /variants/:variantId — начать вариант или продолжить незаконченную попытку */
export const VariantSolvePage = (): JSX.Element => {
    const { variantId = '' } = useParams();
    const id = Number(variantId);
    const queryClient = useQueryClient();
    const { data: attempt, isPending, isError } = useVariantStart(id);
    const onSubmitted = useRefreshAfterSubmit();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [variantId]);

    useEffect(() => () => {
        void queryClient.invalidateQueries({ queryKey: variantKeys.list });
    }, [queryClient]);

    if (isPending && Number.isInteger(id) && id > 0) return <Loading />;
    if (isError || !attempt) return <Missing text="Вариант не найден" />;

    // Новая попытка: сбрасываем кэш — сервер создаст следующую
    const again = () => void queryClient.resetQueries({ queryKey: variantKeys.start(id) });

    return (
        <Container variant='page'>
            <AttemptSolver
                key={attempt.id}
                attempt={attempt}
                back={{ to: VARIANTS_ROUTE, label: 'Каталог вариантов' }}
                kicker={kickerOf(attempt)}
                onSubmitted={onSubmitted}
                resultActions={
                    <>
                        <Button size="m" radius={12} onClick={again}><RotateCcw size={18} />Попробовать снова</Button>
                        <Button as={Link} to={VARIANTS_ROUTE} variant="outline" size="m" radius={12}>
                            <FolderOpen size={18} />В каталог
                        </Button>
                    </>
                }
            />
        </Container>
    );
};


/** /variants/attempts/:attemptId — разбор сданной попытки */
export const VariantAttemptPage = (): JSX.Element => {
    const { attemptId = '' } = useParams();
    const id = Number(attemptId);
    const { data: attempt, isPending, isError } = useVariantAttempt(id);
    const onSubmitted = useRefreshAfterSubmit();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [attemptId]);

    if (isPending && Number.isInteger(id) && id > 0) return <Loading />;
    if (isError || !attempt) return <Missing text="Попытка не найдена" />;

    return (
        <Container variant='page'>
            <AttemptSolver
                key={attempt.id}
                attempt={attempt}
                back={{ to: VARIANTS_ROUTE, label: 'Каталог вариантов' }}
                kicker={kickerOf(attempt)}
                onSubmitted={onSubmitted}
                resultActions={
                    <>
                        <Button as={Link} to={variantSolveRoute(attempt.set.id)} size="m" radius={12}>
                            <RotateCcw size={18} />Решить ещё раз
                        </Button>
                        <Button as={Link} to={VARIANTS_ROUTE} variant="outline" size="m" radius={12}>
                            <FolderOpen size={18} />В каталог
                        </Button>
                    </>
                }
            />
        </Container>
    );
};
