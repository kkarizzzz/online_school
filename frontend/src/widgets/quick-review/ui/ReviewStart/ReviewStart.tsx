import { ArrowUpRight, ChartNoAxesColumn, Flame, ListChecks, Repeat, Target } from 'lucide-react';
import type { JSX } from 'react';
import { cn, percent, plural, pluralize } from '../../../../shared/lib';
import { MODE_ICONS } from '../../lib/modeIcons';
import { ReviewMode } from '../../model/ReviewMode';
import styles from './ReviewStart.module.css';
import type { ReviewStartProps } from './ReviewStart.props';

const accuracyTone = (p: number): string => (p >= 80 ? styles.ok : p >= 50 ? styles.warn : styles.bad);

const formatWhen = (ts: number): string => {
    const d = new Date(ts);
    const time = d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    const dayStart = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
    const days = Math.round((dayStart(new Date()) - dayStart(d)) / 86400000);
    if (days === 0) return `Сегодня, ${time}`;
    if (days === 1) return `Вчера, ${time}`;
    return `${d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })}, ${time}`;
};

const RECENT_SHOWN = 5;


/** Стартовый экран: три режима и статистика прошлых повторений */
export const ReviewStart = ({ questions, history, onStart }: ReviewStartProps): JSX.Element => {
    const summary = history.summary();

    return (
        <section className={styles.start}>
            <div className={styles.modes}>
                {ReviewMode.all.map((mode) => {
                    const Icon = MODE_ICONS[mode.id];
                    const count = mode.poolOf(questions).length;
                    const last = history.lastOf(mode.id);
                    return (
                        <button
                            key={mode.id}
                            type="button"
                            className={cn(styles.mode, { [styles.accent]: mode.isMix })}
                            onClick={() => onStart(mode)}
                        >
                            <span className={styles.glow} />
                            <span className={styles.modeHead}>
                                <span className={styles.modeIcon}><Icon size={26} /></span>
                                <span className={styles.modeArrow}><ArrowUpRight size={22} /></span>
                            </span>
                            <span className={styles.modeBody}>
                                <span className={styles.modeTitle}>{mode.label}</span>
                                <span className={styles.modeDesc}>{mode.description}</span>
                            </span>
                            <span className={styles.modeFoot}>
                                <span>{pluralize(count, 'вопрос', 'вопроса', 'вопросов')}</span>
                                <span className={styles.dot}>&middot;</span>
                                <span>{last ? `В прошлый раз ${percent(last.correct, last.answers)}%` : 'Ещё не проходили'}</span>
                            </span>
                        </button>
                    );
                })}
            </div>

            <section className={cn('glass', styles.history)} aria-labelledby="review-history-title">
                <h2 className={styles.historyTitle} id="review-history-title">Ваши повторения</h2>

                {!summary ? (
                    <div className={styles.historyEmpty}>
                        <ChartNoAxesColumn size={22} />
                        <p>Здесь появится статистика, когда вы ответите хотя бы на один вопрос.</p>
                    </div>
                ) : (
                    <>
                        <div className={styles.tiles}>
                            <Tile icon={<Repeat size={20} />} value={summary.sessions} label={plural(summary.sessions, 'повторение', 'повторения', 'повторений')} />
                            <Tile icon={<ListChecks size={20} />} value={summary.answers} label={plural(summary.answers, 'ответ', 'ответа', 'ответов')} />
                            <Tile icon={<Target size={20} />} value={`${summary.accuracy}%`} label="точность" />
                            <Tile icon={<Flame size={20} />} value={summary.bestStreak} label="лучшая серия" hot />
                        </div>

                        <h3 className={styles.recentTitle}>Последние</h3>
                        <ul className={styles.recent}>
                            {history.recent(RECENT_SHOWN).map((s) => {
                                const mode = ReviewMode.find(s.mode);
                                const Icon = MODE_ICONS[s.mode];
                                const p = percent(s.correct, s.answers);
                                return (
                                    <li key={s.id} className={styles.recentRow}>
                                        <span className={styles.recentIcon}><Icon size={17} /></span>
                                        <span className={styles.recentText}>
                                            <span className={styles.recentMode}>{mode?.label}</span>
                                            <span className={styles.recentWhen}>{formatWhen(s.started)}</span>
                                        </span>
                                        <span className={styles.recentCount}>{s.correct} из {s.answers}</span>
                                        <span className={cn(styles.pill, accuracyTone(p))}>{p}%</span>
                                    </li>
                                );
                            })}
                        </ul>
                    </>
                )}
            </section>
        </section>
    );
};


interface TileProps {
    icon: JSX.Element;
    value: number | string;
    label: string;
    hot?: boolean;
}

const Tile = ({ icon, value, label, hot }: TileProps): JSX.Element => (
    <div className={cn(styles.tile, { [styles.tileHot]: hot })}>
        {icon}
        <span className={styles.tileValue}>{value}</span>
        <span className={styles.tileLabel}>{label}</span>
    </div>
);
