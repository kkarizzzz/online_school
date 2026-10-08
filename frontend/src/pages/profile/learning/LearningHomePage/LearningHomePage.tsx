import type { JSX } from 'react';
import { useLearningProgress } from '../../../../entities/curriculum';
import { NextLesson, UpcomingLessons } from '../../../../entities/lesson';
import { useSubject } from '../../../../entities/subject';
import { useUser } from '../../../../entities/user';
import { SUBJECTS } from '../../../../shared/constants';
import { Container } from '../../../../shared/ui';
import { PageHeader } from '../../../../widgets/page-header';
import { StatsPanel } from '../../../../widgets/statistics-panel';
import { toLessonModel } from '../../../../widgets/theory-route';
import styles from './LearningHomePage.module.css';

const UPCOMING_COUNT = 3;

/** Подпись к кольцу прогресса — по тому, сколько курса пройдено */
const quoteFor = (percent: number): string => {
    if (percent === 0) return '«Каждый эксперт когда-то был новичком. Начни с первого урока.»';
    if (percent < 34) return '«Хорошее начало — главное не останавливаться.»';
    if (percent < 67) return '«Треть пути позади. Дальше будет интереснее.»';
    if (percent < 100) return '«Ты уже на финишной прямой — осталось совсем немного.»';
    return '«Курс пройден! Время закреплять на вариантах.»';
};


export const LearningHomePage = (): JSX.Element => {
    const { data: user } = useUser();
    const { data: progress } = useLearningProgress();

    const currentSubjectId = useSubject();
    const currentSubject = SUBJECTS.find((s) => s.id === currentSubjectId);

    const next = progress?.nextLesson ?? null;
    const upcoming = next ? progress?.curriculum.lessons.slice(next.seq + 1, next.seq + 1 + UPCOMING_COUNT) ?? [] : [];

    return (
        <Container variant='page'>
            <PageHeader title={`С возвращением, ${user?.firstName}`} />

            <main className={styles.grid}>
                {/* Left column */}
                <div className={styles.lessons}>
                    <NextLesson lesson={next && toLessonModel(next)} />
                    {progress && (
                        <UpcomingLessons title='Дальше в программе' lessons={upcoming.map(toLessonModel)} />
                    )}
                </div>

                {/* Right column */}
                <StatsPanel title='Ваш прогресс' subject={currentSubject?.label} progress={progress?.percent ?? 0}>
                    {quoteFor(progress?.percent ?? 0)}
                </StatsPanel>
            </main>
        </Container>
    )
}
