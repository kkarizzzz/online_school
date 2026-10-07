import { useRef, useState, type JSX } from 'react';
import { useObservable } from '../../../../shared/lib';
import { focusNextItem } from '../../lib/focusNextItem';
import { LessonSession } from '../../model/LessonSession';
import { PracticeStep, VideoStep } from '../../model/LessonStep';
import { LessonFinish } from '../LessonFinish/LessonFinish';
import { LessonHeader } from '../LessonHeader/LessonHeader';
import { LessonSidebar } from '../LessonSidebar/LessonSidebar';
import { PracticeStepView } from '../PracticeStepView/PracticeStepView';
import { StepNav } from '../StepNav/StepNav';
import { StepTrack } from '../StepTrack/StepTrack';
import { VideoStepView } from '../VideoStepView/VideoStepView';
import styles from './LessonPlayer.module.css';
import type { LessonPlayerProps } from './LessonPlayer.props';


/**
 * Прохождение урока: ролики → вопросы под каждым → практика → итог.
 * Вся логика — в LessonSession, компоненты только отображают её состояние.
 * Для другого урока компонент нужно пересоздать (key={lesson.id}).
 */
export const LessonPlayer = ({ lesson, lessonContent, nextLesson, onFinish }: LessonPlayerProps): JSX.Element => {
    const [session] = useState(() => new LessonSession(lesson.id, lessonContent.content, onFinish));
    useObservable(session);

    const trackRef = useRef<HTMLOListElement>(null);
    const stageRef = useRef<HTMLElement>(null);

    const go = (stepIndex: number) => {
        if (session.go(stepIndex)) trackRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const handleSolved = (itemIndex: number) => focusNextItem(stageRef.current, session, session.current, itemIndex);

    const stepIndex = session.current;
    const step = session.steps[stepIndex];

    return (
        <div className={styles.player}>
            <LessonHeader
                lesson={lesson}
                session={session}
                title={lessonContent.content.title}
                goal={lessonContent.content.goal}
                isDemo={lessonContent.isDemo}
            />

            <StepTrack ref={trackRef} session={session} onGo={go} />

            <div className={styles.grid}>
                <section className={styles.stage} ref={stageRef} aria-live="polite" key={`${session.epoch}:${stepIndex}`}>
                    {stepIndex === session.finishIndex ? (
                        <LessonFinish session={session} nextLesson={nextLesson} onGo={go} />
                    ) : (
                        <>
                            {step instanceof VideoStep && (
                                <VideoStepView session={session} step={step} stepIndex={stepIndex} onSolved={handleSolved} />
                            )}
                            {step instanceof PracticeStep && (
                                <PracticeStepView session={session} step={step} stepIndex={stepIndex} onSolved={handleSolved} />
                            )}
                            <StepNav session={session} onGo={go} />
                        </>
                    )}
                </section>

                <LessonSidebar session={session} onGo={go} />
            </div>

            <p className={styles.note}>Ответы проверяются в браузере, прогресс урока сохраняется на этом устройстве.</p>
        </div>
    );
};
