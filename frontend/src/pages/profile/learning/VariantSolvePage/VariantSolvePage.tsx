import { useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, FileQuestion, FileText, FolderOpen, Play, RotateCcw, Target } from 'lucide-react';
import { useCallback, useEffect, useState, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import type { AttemptData } from '../../../../entities/attempt';
import { statsKeys } from '../../../../entities/stats';
import {
    VARIANTS_ROUTE, useStartVariant, useVariant, useVariantAttempt, variantKeys, variantSolveRoute, type Variant,
} from '../../../../entities/variant';
import { cn, formatSpentTime, parseApiError, pluralize } from '../../../../shared/lib';
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


/** Факты о варианте на стартовой странице */
const factsOf = (v: Variant): [string, string][] => [
    ['Заданий', v.isStandard
        ? `${v.taskCount} — как на ЕГЭ`
        : `${v.taskCount} — ${v.numbers.length === 1 ? 'задание' : 'задания'} №${v.numbers.join(', ')}`],
    ['Время', v.timeLimitSec ? `${formatSpentTime(v.timeLimitSec)}, таймер` : 'Без ограничения'],
    ['Максимум', v.isStandard
        ? `${pluralize(v.maxScore, 'первичный балл', 'первичных балла', 'первичных баллов')} = 100`
        : pluralize(v.maxScore, 'балл', 'балла', 'баллов')],
    ['Решили', pluralize(v.solvedStudents, 'ученик', 'ученика', 'учеников')],
];

const rulesOf = (v: Variant): string[] => [
    ...(v.isStandard
        ? [
            'Часть 1 (задания 1–12) — краткий ответ, проверяется сразу после сдачи.',
            'Часть 2 (задания 13–19) — развёрнутое решение, его проверит преподаватель.',
        ]
        : ['Между заданиями можно свободно переключаться.']),
    v.timeLimitSec
        ? 'Таймер запустится, как только вы приступите. Когда время выйдет, вариант сдастся сам.'
        : 'Таймера нет — решайте в своём темпе.',
    'Попытку нельзя отложить: если уйти со страницы, продолжить её не получится — только начать заново.',
    'После сдачи — баллы и разбор по каждому заданию.',
];


/** Стартовая страница: факты, правила и «Приступить к варианту» */
const VariantIntro = ({ variant, starting, error, onStart }: {
    variant: Variant;
    starting: boolean;
    error: string | null;
    onStart: () => void;
}): JSX.Element => (
    <div className={styles.solve}>
        <header className={cn('glass', styles.top)}>
            <Link className={styles.back} to={VARIANTS_ROUTE}>
                <ArrowLeft size={18} /><span>Каталог вариантов</span>
            </Link>
            <div className={styles.heading}>
                <p className={styles.kicker}>
                    {variant.isStandard ? 'Вариант ЕГЭ' : 'Отработка'} · {pluralize(variant.taskCount, 'задание', 'задания', 'заданий')}
                </p>
                <h1 className={styles.title}>{variant.title}</h1>
            </div>
        </header>

        <section className={cn('glass', styles.intro)}>
            <div className={styles.introHead}>
                <span className={styles.introIcon} aria-hidden="true">
                    {variant.isStandard ? <FileText size={24} /> : <Target size={24} />}
                </span>
                <div>
                    <p className={styles.introKicker}>Перед началом</p>
                    <h2 className={styles.introTitle}>{variant.title}</h2>
                </div>
            </div>

            {variant.description && <p className={styles.introText}>{variant.description}</p>}

            <dl className={styles.facts}>
                {factsOf(variant).map(([k, val]) => (
                    <div key={k}><dt>{k}</dt><dd>{val}</dd></div>
                ))}
            </dl>

            <ul className={styles.rules}>
                {rulesOf(variant).map((r) => <li key={r}>{r}</li>)}
            </ul>

            <div className={styles.introActions}>
                <Button size="m" radius={12} className={styles.startBtn} onClick={onStart} disabled={starting}>
                    <Play size={18} />{starting ? 'Начинаем…' : 'Приступить к варианту'}
                </Button>
                <p className={error ? styles.introError : styles.introHint} role={error ? 'alert' : undefined}>
                    {error ?? (variant.timeLimitSec
                        ? `Таймер на ${formatSpentTime(variant.timeLimitSec)} запустится сразу.`
                        : 'Таймера нет — секундомер просто покажет, сколько прошло.')}
                </p>
            </div>
        </section>
    </div>
);


/**
 * /variants/:variantId — стартовая страница варианта, «Приступить к варианту» начинает новую попытку.
 * Начатую попытку продолжить нельзя: после перезагрузки снова стартовая страница.
 */
export const VariantSolvePage = (): JSX.Element => {
    const { variantId = '' } = useParams();
    const id = Number(variantId);
    const queryClient = useQueryClient();
    const { data: variant, isPending, isError } = useVariant(id);
    const start = useStartVariant();
    const [attempt, setAttempt] = useState<AttemptData | null>(null);
    const [submitted, setSubmitted] = useState(false);
    const refresh = useRefreshAfterSubmit();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [variantId, attempt]);

    useEffect(() => () => {
        void queryClient.invalidateQueries({ queryKey: variantKeys.list });
    }, [queryClient]);

    // Идёт решение — перезагрузка или закрытие вкладки сначала спрашивают подтверждение
    const solving = attempt !== null && !submitted;
    useEffect(() => {
        if (!solving) return;
        const warn = (e: BeforeUnloadEvent) => e.preventDefault();
        window.addEventListener('beforeunload', warn);
        return () => window.removeEventListener('beforeunload', warn);
    }, [solving]);

    const onSubmitted = useCallback(() => {
        setSubmitted(true);
        refresh();
        void queryClient.invalidateQueries({ queryKey: variantKeys.one(id) });
    }, [refresh, queryClient, id]);

    const begin = () => start.mutate(id, {
        onSuccess: (data) => {
            setSubmitted(false);
            setAttempt(data);
        },
    });

    // «Попробовать снова» — обратно на стартовую страницу
    const again = () => {
        start.reset();
        setAttempt(null);
    };

    if (isPending && Number.isInteger(id) && id > 0) return <Loading />;
    if (isError || !variant) return <Missing text="Вариант не найден" />;

    if (!attempt) {
        return (
            <Container variant='page'>
                <VariantIntro
                    variant={variant}
                    starting={start.isPending}
                    error={start.isError ? parseApiError(start.error, 'Не удалось начать вариант — попробуйте ещё раз') : null}
                    onStart={begin}
                />
            </Container>
        );
    }

    return (
        <Container variant='page'>
            <AttemptSolver
                key={attempt.id}
                attempt={attempt}
                back={{ to: VARIANTS_ROUTE, label: 'Каталог вариантов' }}
                kicker={kickerOf(attempt)}
                onSubmitted={onSubmitted}
                resumable={false}
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
