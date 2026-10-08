import { CheckCircle2, Clock } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { Card } from '../../../../shared/ui';
import { lessonRoute } from '../../lib/routes';
import styles from './UpcomingLessons.module.css';
import type { UpcomingLessonsProps } from './UpcomingLessons.props';


export const UpcomingLessons = ({ 
    title,
    lessons, 
    className, 
    ...props 
}: UpcomingLessonsProps): JSX.Element => {

    const isDone = !lessons || lessons.length === 0;

    return (
        <Card variant="glass" className={className} {...props}>
            <h3 className={styles.title}>{title}</h3>
            
            {isDone ? (
                <div className={styles.emptyState}>
                    <CheckCircle2 size={32} opacity={0.5} />
                    <span>Всё выполнено, ожидайте обновлений!</span>
                </div>            
            ) : (
                <ul className={styles.list}>
                    {lessons.map((lesson) => (
                        <li key={lesson.id}>
                            <Link to={lessonRoute(lesson.id)} className={styles.item}>
                                <CheckCircle2 className={styles.icon} />
                                
                                <span className={styles.itemTitle}>{lesson.title}</span>

                                <span className={styles.itemTime}>
                                    <Clock size={14} />
                                    {lesson.duration} мин
                                </span>
                            </Link>
                        </li>
                    ))}
                </ul>
            )}
        </Card>
    );
};