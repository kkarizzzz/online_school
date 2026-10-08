import { Flame, ListChecks, Target } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useEffect, useState, type JSX } from 'react';
import { useSearchParams } from 'react-router';
import { useReviewQuestions, type ReviewQuestion } from '../../../../entities/review-question';
import { useObservable } from '../../../../shared/lib';
import { FeedBar } from '../../../../shared/ui';
import { MODE_ICONS } from '../../lib/modeIcons';
import { ReviewFeed } from '../../model/ReviewFeed';
import { ReviewHistory } from '../../model/ReviewHistory';
import { ReviewMode } from '../../model/ReviewMode';
import { ReviewCardView } from '../ReviewCardView/ReviewCardView';
import { ReviewStart } from '../ReviewStart/ReviewStart';
import styles from './QuickReview.module.css';


/** «Быстрое повторение»: выбор режима → бесконечная лента коротких вопросов */
export const QuickReview = (): JSX.Element => {
    const { data: questions, isError } = useReviewQuestions();
    // История — один раз на открытие страницы; дальше её дополняет сама лента
    const { data: history, isError: historyError } = useQuery({
        queryKey: ['review', 'sessions'],
        queryFn: () => ReviewHistory.load(),
        staleTime: Infinity,
        gcTime: 0,
    });

    return (
        <div className={styles.wrapper}>
            {isError || historyError ? (
                <p className={styles.empty}>Не удалось загрузить вопросы. Обновите страницу.</p>
            ) : questions && history ? (
                <QuickReviewFeed questions={questions} history={history} />
            ) : (
                <p className={styles.empty}>Загружаем вопросы…</p>
            )}
            <p className={styles.note}>
                Ответ проверяется сразу, история повторений сохраняется в вашем профиле. Позже вопросы будет подбирать алгоритм повторения.
            </p>
        </div>
    );
};


const QuickReviewFeed = ({ questions, history }: { questions: ReviewQuestion[]; history: ReviewHistory }): JSX.Element => {
    const [params, setParams] = useSearchParams();
    // ?mode=theory|calc|mix — продолжить ленту после перезагрузки
    const [feed] = useState(() => {
        const created = new ReviewFeed(questions, history);
        const mode = ReviewMode.find(params.get('mode'));
        if (mode) created.start(mode);
        return created;
    });
    useObservable(feed);

    const { mode, session, card } = feed;

    useEffect(() => {
        setParams(mode ? { mode: mode.id } : {}, { replace: true });
    }, [mode, setParams]);

    const start = (picked: ReviewMode) => {
        feed.start(picked);
        window.scrollTo({ top: 0 });
    };

    const back = () => {
        feed.exit();
        window.scrollTo({ top: 0 });
    };

    if (!mode || !session || !card) {
        return <ReviewStart questions={questions} history={history} onStart={start} />;
    }

    const ModeIcon = MODE_ICONS[mode.id];

    return (
        <section className={styles.feed}>
            <FeedBar
                backLabel="Режимы"
                onBack={back}
                modeIcon={<ModeIcon size={18} />}
                modeAccent={mode.isMix}
                modeLabel="Повторение"
                modeTitle={mode.label}
                stats={[
                    { icon: ListChecks, label: 'Ответов', value: session.answers, title: 'Ответов за это повторение' },
                    { icon: Target, label: 'Точность', value: session.answers ? `${session.accuracy}%` : '—', title: 'Доля верных ответов' },
                    { icon: Flame, label: 'Серия', value: session.streak, title: 'Верных ответов подряд', hot: true, bumpKey: session.streak },
                ]}
            />
            <ReviewCardView key={card.number} feed={feed} card={card} />
        </section>
    );
};
