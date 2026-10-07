import { CirclePlay, Info, ListOrdered, PencilLine } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { cn, formatDuration, pluralize } from '../../../../shared/lib';
import styles from './LessonHeader.module.css';
import type { LessonHeaderProps } from './LessonHeader.props';


export const LessonHeader = ({ lesson, session, title, goal, isDemo, className, ...props }: LessonHeaderProps): JSX.Element => {
    const topic = lesson.topic;

    return (
        <div className={cn(styles.header, className)} {...props}>
            <p className={styles.crumb}>
                <Link to="/profile/learning/theory">Теория</Link> &middot; Уровень {topic.level} &middot; {topic.title}
            </p>
            <h1 className={styles.title}>{lesson.id}. {isDemo ? lesson.name : title}</h1>
            <p className={styles.goal}>{goal}</p>

            <p className={styles.meta}>
                <span>
                    <CirclePlay size={16} />
                    {pluralize(session.videos.length, 'ролик', 'ролика', 'роликов')} &middot; {formatDuration(session.videoSeconds)}
                </span>
                <span><PencilLine size={16} />{pluralize(session.practiceTaskCount, 'задача', 'задачи', 'задач')}</span>
                <span><ListOrdered size={16} />Урок {lesson.index} из {topic.lessons.length}</span>
                {topic.examTasks.map((n) => <span key={n} className={styles.tag}>№{n} ЕГЭ</span>)}
            </p>

            {isDemo && (
                <div className={styles.demo}>
                    <Info size={18} />
                    <p>Роликов к этому уроку пока нет — показан демо-урок <b>«{title}»</b>, чтобы посмотреть, как проходит урок.</p>
                </div>
            )}
        </div>
    );
};
