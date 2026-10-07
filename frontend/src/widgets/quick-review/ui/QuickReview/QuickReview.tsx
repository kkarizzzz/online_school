import { Flame, ListChecks, Target } from 'lucide-react';
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
    const { data: questions } = useReviewQuestions();

    return (
        <div className={styles.wrapper}>
            {questions ? <QuickReviewFeed questions={questions} /> : <p className={styles.empty}>Загружаем вопросы…</p>}
            <p className={styles.note}>
                Ответы проверяются в браузере, статистика хранится на этом устройстве. Позже вопросы будет подбирать алгоритм повторения.
            </p>
        </div>
    );
};


const QuickReviewFeed = ({ questions }: { questions: ReviewQuestion[] }): JSX.Element => {
    const [params, setParams] = useSearchParams();
    const [history] = useState(() => new ReviewHistory());
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
