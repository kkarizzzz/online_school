import { useEffect, type JSX } from 'react';
import { Link, useParams } from 'react-router';
import { useCompleteLesson, useLearningProgress } from '../../../../entities/curriculum';
import { useLessonContent } from '../../../../entities/lesson';
import { Container } from '../../../../shared/ui';
import { LessonPlayer } from '../../../../widgets/lesson-player';
import styles from './LessonPage.module.css';


export const LessonPage = (): JSX.Element => {
    const { lessonId = '' } = useParams();
    const { data: progress, isPending } = useLearningProgress();
    const { data: lessonContent } = useLessonContent(lessonId);
    const { mutate: completeLesson } = useCompleteLesson();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [lessonId]);

    const lesson = progress?.curriculum.lesson(lessonId);

    if (!isPending && !lesson) {
        return (
            <Container variant='page'>
                <div className={styles.message}>
                    <p>Урок {lessonId} не найден в программе.</p>
                    <Link to="/profile/learning/theory">Вернуться к маршруту</Link>
                </div>
            </Container>
        );
    }

    if (!progress || !lesson || !lessonContent) {
        return (
            <Container variant='page'>
                <p className={styles.message}>Загружаем урок…</p>
            </Container>
        );
    }

    return (
        <Container variant='page'>
            <LessonPlayer
                key={lesson.id}
                lesson={lesson}
                lessonContent={lessonContent}
                nextLesson={progress.curriculum.lessonAfter(lesson)}
                onFinish={(score) => completeLesson({ lessonId: lesson.id, percent: score })}
            />
        </Container>
    );
};
