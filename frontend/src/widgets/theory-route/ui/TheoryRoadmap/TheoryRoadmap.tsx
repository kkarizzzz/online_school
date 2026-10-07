import { CircleCheck, LayoutGrid, ListOrdered, MapPin, SearchIcon } from 'lucide-react';
import { useCallback, useRef, useState, type JSX } from 'react';
import type { Lesson, Topic } from '../../../../entities/curriculum';
import { cn, plural, pluralize, useObservable } from '../../../../shared/lib';
import { ProgressBar } from '../../../../shared/ui';
import { TheoryRouteState, type RouteView, type StatusFilter } from '../../model/TheoryRouteState';
import { CurriculumMap } from '../CurriculumMap/CurriculumMap';
import { LessonDrawer } from '../LessonDrawer/LessonDrawer';
import { RouteList } from '../RouteList/RouteList';
import { TheoryOverview } from '../TheoryOverview/TheoryOverview';
import styles from './TheoryRoadmap.module.css';
import type { TheoryRoadmapProps } from './TheoryRoadmap.props';

const STATUS_CHIPS: { id: StatusFilter; label: string }[] = [
    { id: 'all', label: 'Все' },
    { id: 'progress', label: 'В процессе' },
    { id: 'todo', label: 'Не начаты' },
    { id: 'done', label: 'Завершены' },
];

const VIEWS: { id: RouteView; label: string; icon: typeof ListOrdered }[] = [
    { id: 'route', label: 'Маршрут', icon: ListOrdered },
    { id: 'map', label: 'Карта', icon: LayoutGrid },
];


/** Вкладка «Теория»: маршрут по программе от базы к профилю, карта тем и конспекты уроков */
export const TheoryRoadmap = ({ progress }: TheoryRoadmapProps): JSX.Element => {
    const [state] = useState(() => new TheoryRouteState(progress));
    useObservable(state);

    const [searchText, setSearchText] = useState('');
    const [drawer, setDrawer] = useState<{ lesson: Lesson | null; open: boolean }>({ lesson: null, open: false });
    const routeRef = useRef<HTMLElement>(null);

    const { curriculum } = progress;
    const currentLevel = progress.nextLesson?.topic.level;

    const openLesson = (lesson: Lesson) => setDrawer({ lesson, open: true });
    const closeDrawer = useCallback(() => setDrawer((d) => ({ ...d, open: false })), []);

    const selectLevel = (level: number, scroll = false) => {
        setSearchText('');
        state.selectLevel(level);
        if (scroll) routeRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const goToTopic = (topic: Topic) => {
        setSearchText('');
        state.goToTopic(topic);
        requestAnimationFrame(() => {
            document.getElementById(`topic-${topic.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    };

    const search = (value: string) => {
        setSearchText(value);
        state.search(value, progress);
    };

    const levelTopics = curriculum.topicsOf(state.level);
    const visible = state.countVisible(progress);
    const filterNote = state.query
        ? `По запросу «${state.query}»: ${pluralize(visible, 'тема', 'темы', 'тем')} на всех уровнях`
        : `Уровень ${state.level}: ${progress.countTopics(levelTopics).done} из ${levelTopics.length} тем завершено`;

    return (
        <>
            <TheoryOverview progress={progress} onSelectLevel={(level) => selectLevel(level, true)} />

            <section className={styles.route} ref={routeRef} aria-labelledby="route-title">
                <div className={styles.head}>
                    <div>
                        <h2 className={styles.title} id="route-title">Маршрут подготовки</h2>
                        <p className={styles.muted}>Уровень → ветка 1–5 → тема. Можно перескакивать, но мы советуем идти по порядку.</p>
                    </div>
                    <div className={styles.segmented} role="tablist" aria-label="Вид">
                        {VIEWS.map(({ id, label, icon: Icon }) => (
                            <button key={id} type="button" role="tab" aria-selected={state.view === id} onClick={() => state.setView(id)}>
                                <Icon size={16} />{label}
                            </button>
                        ))}
                    </div>
                </div>

                {state.view === 'route' ? (
                    <>
                        <div className={styles.levelTabs} role="tablist" aria-label="Уровень">
                            {curriculum.levels.map((level, i) => {
                                const { done, total } = progress.countLessons(curriculum.lessonsOfLevel(i));
                                const topicsCount = curriculum.topicsOf(i).length;
                                const isDone = done === total;
                                return (
                                    <button
                                        key={level.name}
                                        type="button"
                                        role="tab"
                                        className={styles.levelTab}
                                        aria-selected={i === state.level && !state.query}
                                        onClick={() => selectLevel(i)}
                                    >
                                        <span className={styles.ltTop}>
                                            <span className={styles.ltNum}>Уровень {i}</span>
                                            {isDone ? (
                                                <span className={cn(styles.ltState, styles.ltDone)}><CircleCheck size={14} />Пройден</span>
                                            ) : i === currentLevel ? (
                                                <span className={cn(styles.ltState, styles.ltCurrent)}><MapPin size={14} />Вы здесь</span>
                                            ) : (
                                                <span className={styles.ltState}>{done}/{total} уроков</span>
                                            )}
                                        </span>
                                        <span className={styles.ltName}>{level.name}</span>
                                        <span className={styles.ltDesc}>{level.desc} &middot; {topicsCount} {plural(topicsCount, 'тема', 'темы', 'тем')}</span>
                                        <ProgressBar value={done} max={total} tone={isDone ? 'done' : 'primary'} />
                                    </button>
                                );
                            })}
                        </div>

                        <div className={styles.filters}>
                            <div className={styles.chips}>
                                {STATUS_CHIPS.map(({ id, label }) => (
                                    <button
                                        key={id}
                                        type="button"
                                        className={styles.chip}
                                        aria-pressed={state.status === id}
                                        onClick={() => state.setStatus(id)}
                                    >
                                        {label}
                                    </button>
                                ))}
                            </div>
                            <label className={styles.search}>
                                <SearchIcon size={16} />
                                <input
                                    type="search"
                                    value={searchText}
                                    onChange={(e) => search(e.target.value)}
                                    placeholder="Поиск по темам и урокам…"
                                    aria-label="Поиск по темам и урокам"
                                />
                            </label>
                        </div>
                        <p className={styles.note}>{filterNote}</p>

                        <RouteList progress={progress} state={state} onOpenLesson={openLesson} />
                    </>
                ) : (
                    <CurriculumMap progress={progress} onSelectTopic={goToTopic} />
                )}
            </section>

            <LessonDrawer lesson={drawer.lesson} open={drawer.open} progress={progress} onClose={closeDrawer} />
        </>
    );
};
