import { ArrowRight, Clock } from 'lucide-react';
import { type JSX } from 'react';
import { Link } from 'react-router';
import { cn } from '../../../../shared/lib';
import { lessonRoute } from '../../lib/routes';
import styles from './NextLesson.module.css';
import type { NextLessonProps } from './NextLesson.props';


export const NextLesson = ({ lesson, className, ...props }: NextLessonProps): JSX.Element | null => {
    
    if (!lesson) return null;

    return (
        <Link 
            to={lessonRoute(lesson.id)} 
            className={cn(styles.card, className)} 
            {...props} 
        >
            <div className={styles.content}>
                <span className={styles.badge}>
                    <span className={styles.dot} />
                    Модуль {lesson.moduleNumber} &middot; {lesson.moduleTopic}
                </span>
                
                <h2 className={styles.title}>
                    {lesson.title}
                </h2>
                
                <p className={styles.metaInfo}>
                    <Clock size={16} />
                    Осталось примерно {lesson.duration} минут &middot; Урок {lesson.lessonNumber} из {lesson.lessonTotal}
                </p>
            </div>

            <div className={styles.footer}>
                <span className={styles.footerText}>
                    Перейти к следующему уроку
                </span>
                <span className={styles.arrowBtn}>
                    <ArrowRight size={20} />
                </span>
            </div>
        </Link>
    );
};