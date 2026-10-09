import { ArrowUpRight, History, Play, Plus, Settings2, Star, Tornado } from 'lucide-react';
import type { JSX } from 'react';
import { useNavigate } from 'react-router';
import type { PracticeNumber } from '../../../../entities/practice-task';
import { cn, pluralize } from '../../../../shared/lib';
import { Button, ProgressBar } from '../../../../shared/ui';
import type { PersonalSelection, PersonalStorage, RecentSelection } from '../../model/PersonalStorage';
import { countTasks, describeDifficulties, describeTopics, PERSONAL_ROUTE, TORNADO, type PracticeScope } from '../../model/scope';
import styles from './PracticeHome.module.css';

interface PracticeHomeProps {
    numbers: PracticeNumber[];
    storage: PersonalStorage;
    onStart: (scope: PracticeScope) => void;
}

const tasksWord = (n: number) => pluralize(n, 'задание', 'задания', 'заданий');

/** Состав подборки и сложность одной строкой */
const summary = (numbers: PracticeNumber[], s: PersonalSelection): string => {
    const levels = describeDifficulties(s.difficulties);
    return describeTopics(numbers, s.topicIds) + (levels ? ` · сложность: ${levels}` : '');
};

/** Когда запускали: «сегодня, 14:05», «вчера, 09:30», «7 октября» */
const whenText = (ms: number): string => {
    const date = new Date(ms);
    const days = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(ms).setHours(0, 0, 0, 0)) / 86_400_000);
    const time = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    if (days === 0) return `сегодня, ${time}`;
    if (days === 1) return `вчера, ${time}`;
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
};


/**
 * Главная нарешки: «Торнадо» по первой части, персональный режим и три последние подборки.
 * Номера ЕГЭ здесь не показываются — их выбирают на странице настройки персонального режима.
 */
export const PracticeHome = ({ numbers, storage, onStart }: PracticeHomeProps): JSX.Element => {
    const navigate = useNavigate();
    const personal = storage.read();
    const recent = storage.recent().filter((r) => countTasks(numbers, r.topicIds, []).total > 0);

    const tornado = countTasks(numbers, null, [], 1);
    const mine = countTasks(numbers, personal.topicIds, personal.difficulties);
    const hasPersonal = personal.topicIds.length > 0;

    /** Подборку из истории делаем персональной: решать её или поправить */
    const applyRecent = (r: RecentSelection, edit: boolean) => {
        storage.write({ topicIds: r.topicIds, difficulties: r.difficulties });
        if (edit) navigate(PERSONAL_ROUTE);
        else onStart(storage.scope());
    };

    return (
        <section className={styles.home}>
            <div className={styles.modes}>
                <button type="button" className={cn(styles.card, styles.accent)} onClick={() => onStart(TORNADO)}>
                    <span className={styles.cardHead}>
                        <span className={styles.cardIcon}><Tornado size={24} /></span>
                        <ArrowUpRight size={22} className={styles.cardArrow} />
                    </span>
                    <span className={styles.cardEyebrow}>Номера 1–12 · {tasksWord(tornado.total)}</span>
                    <span className={styles.cardTitle}>Торнадо</span>
                    <span className={styles.cardDesc}>
                        Задачи из всех номеров первой части вперемешку — как на экзамене, где не знаешь, что попадётся следующим.
                    </span>
                    <Progress solved={tornado.solved} total={tornado.total} light />
                </button>

                <div className={styles.card}>
                    <span className={styles.cardHead}>
                        <span className={styles.cardIcon}><Star size={24} /></span>
                    </span>
                    <span className={styles.cardEyebrow}>{hasPersonal ? tasksWord(mine.total) : 'Пока пусто'}</span>
                    <span className={styles.cardTitle}>Персональный</span>
                    <span className={styles.cardDesc}>
                        {hasPersonal ? summary(numbers, personal) : 'Соберите свои номера и подтемы, выберите сложность — и решайте только их.'}
                    </span>
                    {hasPersonal && <Progress solved={mine.solved} total={mine.total} />}
                    <span className={styles.cardActions}>
                        {hasPersonal && (
                            <Button
                                size="m"
                                disabled={!mine.total}
                                title={mine.total ? undefined : 'Нет заданий выбранной сложности'}
                                onClick={() => onStart(storage.scope())}
                            >
                                <Play size={18} />Решать
                            </Button>
                        )}
                        <Button variant={hasPersonal ? 'outline' : 'primary'} size="m" onClick={() => navigate(PERSONAL_ROUTE)}>
                            {hasPersonal ? <><Settings2 size={18} />Изменить</> : <><Plus size={18} />Собрать подборку</>}
                        </Button>
                    </span>
                </div>
            </div>

            {recent.length > 0 && (
                <section className={styles.recent} aria-labelledby="practice-recent">
                    <h2 className={styles.sectionTitle} id="practice-recent">Последние подборки</h2>
                    <ul className={styles.recentList}>
                        {recent.map((r) => {
                            const tasks = countTasks(numbers, r.topicIds, r.difficulties);
                            const levels = describeDifficulties(r.difficulties);
                            const current = storage.isCurrent(r);
                            return (
                                <li key={r.at} className={cn('glass', styles.recentItem, { [styles.current]: current })}>
                                    <span className={styles.recentIcon}><History size={18} /></span>
                                    <span className={styles.recentText}>
                                        <span className={styles.recentTitle}>{describeTopics(numbers, r.topicIds)}</span>
                                        <span className={styles.recentMeta}>
                                            {[levels && `Сложность: ${levels}`, tasksWord(tasks.total), whenText(r.at),
                                                current && 'сейчас в персональном'].filter(Boolean).join(' · ')}
                                        </span>
                                    </span>
                                    <Progress solved={tasks.solved} total={tasks.total} className={styles.recentProgress} />
                                    <span className={styles.recentActions}>
                                        <Button variant="ghost-secondary" size="s" onClick={() => applyRecent(r, true)}>
                                            <Settings2 size={16} />Изменить
                                        </Button>
                                        <Button variant="outline" size="s" disabled={!tasks.total} onClick={() => applyRecent(r, false)}>
                                            <Play size={16} />Решать
                                        </Button>
                                    </span>
                                </li>
                            );
                        })}
                    </ul>
                </section>
            )}
        </section>
    );
};


interface ProgressProps {
    solved: number;
    total: number;
    light?: boolean;
    className?: string;
}

/** Полоска «решено из» — только на главной, в самой ленте общего числа заданий не видно */
const Progress = ({ solved, total, light, className }: ProgressProps): JSX.Element => (
    <span className={cn(styles.progress, { [styles.light]: light }, className)} title={`Решено ${solved} из ${total}`}>
        <ProgressBar value={solved} max={total} size="s" tone={light ? 'var(--white)' : solved === total && total ? 'done' : 'primary'} />
        <span className={styles.progressNum}>{solved}<span>/{total}</span></span>
    </span>
);
