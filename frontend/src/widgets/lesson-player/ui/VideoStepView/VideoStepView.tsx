import { Captions, Check, Eye } from 'lucide-react';
import { useRef, type JSX } from 'react';
import { cn, formatDuration, plural } from '../../../../shared/lib';
import { ItemCard } from '../ItemCard/ItemCard';
import styles from './VideoStepView.module.css';
import type { VideoStepViewProps } from './VideoStepView.props';

/** Просмотр засчитывается с 90% — финальная шпаргалка часто стоит на паузе */
const WATCHED_SHARE = 0.9;


export const VideoStepView = ({ session, step, stepIndex, onSolved }: VideoStepViewProps): JSX.Element => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const watched = session.isWatched(stepIndex);
    const number = session.videos.indexOf(step) + 1;

    const handleTimeUpdate = () => {
        const v = videoRef.current;
        if (v?.duration && v.currentTime / v.duration > WATCHED_SHARE) session.markWatched(stepIndex);
    };

    const rewatch = () => {
        const v = videoRef.current;
        if (!v) return;
        v.currentTime = 0;
        v.play().catch(() => {});
        v.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };

    return (
        <>
            <article className={cn('glass', styles.card)}>
                <div className={styles.head}>
                    <div>
                        <p className={styles.kicker}>Ролик {number} из {session.videos.length} &middot; {formatDuration(step.duration)}</p>
                        <h2 className={styles.title}>{step.title}</h2>
                    </div>
                    <span className={cn(styles.pill, { [styles.pillOk]: watched })}>
                        {watched ? <><Check size={13} />Просмотрено</> : <><Eye size={13} />Не просмотрено</>}
                    </span>
                </div>

                <div className={styles.player}>
                    <video
                        ref={videoRef}
                        controls
                        playsInline
                        preload="metadata"
                        poster={step.poster}
                        src={step.src}
                        onTimeUpdate={handleTimeUpdate}
                        onEnded={() => session.markWatched(stepIndex)}
                    />
                </div>

                <details className={styles.transcript}>
                    <summary><Captions size={18} />Текст ролика</summary>
                    <ul>
                        {step.transcript.map((line) => <li key={line}>{line}</li>)}
                    </ul>
                </details>
            </article>

            <section className={styles.checks}>
                <div className={styles.checksHead}>
                    <h3 className={styles.checksTitle}>Проверь себя</h3>
                    <p className={styles.muted}>
                        Ответьте на {plural(step.items.length, 'вопрос', 'вопросы', 'вопросы')} по ролику — после этого откроется следующий шаг.
                    </p>
                </div>
                {step.items.map((_, ii) => (
                    <ItemCard
                        key={ii}
                        session={session}
                        stepIndex={stepIndex}
                        itemIndex={ii}
                        onSolved={onSolved}
                        onRewatch={rewatch}
                    />
                ))}
            </section>
        </>
    );
};
