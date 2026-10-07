import type { CSSProperties, JSX } from 'react';
import { plural } from '../../../../shared/lib';
import { TopicItem } from '../TopicItem/TopicItem';
import styles from './RouteList.module.css';
import type { RouteListProps } from './RouteList.props';


/** Темы, сгруппированные по ветке (а при поиске — ещё и по уровню) */
export const RouteList = ({ progress, state, onOpenLesson }: RouteListProps): JSX.Element => {
    const { curriculum } = progress;
    const groups = state.groups(progress);

    if (!groups.length) {
        return <div className={styles.empty}>Здесь пока пусто — попробуйте другой фильтр.</div>;
    }

    return (
        <div>
            {groups.map(({ level, branches }) => (
                <div key={level}>
                    {state.query && (
                        <h3 className={styles.levelTitle}>Уровень {level} &middot; {curriculum.levels[level].name}</h3>
                    )}
                    {branches.map(({ branch, topics }) => {
                        const branchCount = progress.countTopics(curriculum.topicsOf(level, branch));
                        return (
                            <div key={branch} className={styles.branch} style={{ '--c': `var(--b${branch + 1})` } as CSSProperties}>
                                <div className={styles.branchHead}>
                                    <span className={styles.dot} />
                                    <span className={styles.branchName}>
                                        <span>Ветка {branch + 1}</span>
                                        {curriculum.branches[branch]}
                                    </span>
                                    <span className={styles.branchCount}>
                                        {branchCount.done}/{branchCount.total} {plural(branchCount.total, 'тема', 'темы', 'тем')}
                                    </span>
                                </div>
                                <ol className={styles.topics}>
                                    {topics.map((topic) => (
                                        <TopicItem
                                            key={topic.id}
                                            topic={topic}
                                            progress={progress}
                                            state={state}
                                            onOpenLesson={onOpenLesson}
                                        />
                                    ))}
                                </ol>
                            </div>
                        );
                    })}
                </div>
            ))}
        </div>
    );
};
