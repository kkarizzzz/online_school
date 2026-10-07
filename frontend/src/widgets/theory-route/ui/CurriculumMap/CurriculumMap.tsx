import { Fragment, type CSSProperties, type JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { ProgressBar } from '../../../../shared/ui';
import styles from './CurriculumMap.module.css';
import type { CurriculumMapProps } from './CurriculumMap.props';

const branchColor = (branch: number) => ({ '--c': `var(--b${branch + 1})` } as CSSProperties);


/** Матрица «ветка × уровень»: вся программа на одном экране */
export const CurriculumMap = ({ progress, onSelectTopic }: CurriculumMapProps): JSX.Element => {
    const { curriculum } = progress;

    return (
        <>
            <div className={styles.legend}>
                <span><i className={cn(styles.lg, styles.lgDone)} />Завершена</span>
                <span><i className={cn(styles.lg, styles.lgProgress)} />В процессе</span>
                <span><i className={cn(styles.lg, styles.lgNext)} />Следующая</span>
                <span><i className={styles.lg} />Не начата</span>
            </div>

            <div className={styles.scroll}>
                <div className={styles.map}>
                    <div />
                    {curriculum.branches.map((name, branch) => {
                        const { done, total } = progress.countLessons(curriculum.lessonsOfBranch(branch));
                        return (
                            <div key={name} className={styles.branchHead} style={branchColor(branch)}>
                                <span>Ветка {branch + 1}</span>
                                <b>{name}</b>
                                <ProgressBar className={styles.branchBar} value={done} max={total} tone="var(--c)" size="s" />
                            </div>
                        );
                    })}

                    {curriculum.levels.map((level, li) => (
                        <Fragment key={level.name}>
                            <div className={styles.levelLabel}><b>Уровень {li}</b><span>{level.name}</span></div>
                            {curriculum.branches.map((name, branch) => {
                                const topics = curriculum.topicsOf(li, branch);
                                if (!topics.length) {
                                    return <div key={name} className={cn(styles.cell, styles.none)} style={branchColor(branch)}>нет уровня</div>;
                                }
                                return (
                                    <div key={name} className={styles.cell} style={branchColor(branch)}>
                                        {topics.map((topic) => {
                                            const status = progress.statusOf(topic);
                                            return (
                                                <button
                                                    key={topic.id}
                                                    type="button"
                                                    className={cn(styles.tile, styles[status], { [styles.next]: progress.isNextTopic(topic) })}
                                                    title={topic.name}
                                                    onClick={() => onSelectTopic(topic)}
                                                >
                                                    <span className={styles.tileId}>{topic.id}</span>
                                                    <span>{topic.name}</span>
                                                    {status !== 'done' && (
                                                        <ProgressBar
                                                            className={styles.tileBar}
                                                            value={progress.doneIn(topic)}
                                                            max={topic.lessons.length}
                                                            size="s"
                                                        />
                                                    )}
                                                </button>
                                            );
                                        })}
                                    </div>
                                );
                            })}
                        </Fragment>
                    ))}
                </div>
            </div>
        </>
    );
};
