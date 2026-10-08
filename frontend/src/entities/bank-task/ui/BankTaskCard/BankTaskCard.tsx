import { Calendar, Circle, CircleCheck, Eye, EyeOff, Lightbulb, Users } from 'lucide-react';
import { useState, type JSX } from 'react';
import { cn, formatLongDate, plural } from '../../../../shared/lib';
import { Markdown, MathText } from '../../../../shared/ui';
import { LevelMeter } from '../LevelMeter/LevelMeter';
import styles from './BankTaskCard.module.css';
import type { BankTaskCardProps } from './BankTaskCard.props';


/** Задание банка: код, тема, сложность, условие, ответ с решением по кнопке и отметка «решено».
 * Решённое засчитанным ответом (в нарешке, ДЗ, варианте) отметку не снимает */
export const BankTaskCard = ({ task, code, topicName, solved, onToggleSolved }: BankTaskCardProps): JSX.Element => {
    const [answerShown, setAnswerShown] = useState(false);
    const solvedBy = task.solvedBy.toLocaleString('ru-RU');

    return (
        <li className={cn('glass', styles.task, { [styles.isSolved]: solved })}>
            <div className={styles.head}>
                <span className={styles.code}>{code}</span>
                <span className={styles.topic}>{topicName}</span>
                <LevelMeter level={task.level} />
                <span className={styles.facts}>
                    <span title={`Решили ${solvedBy} ${plural(task.solvedBy, 'ученик', 'ученика', 'учеников')}`}>
                        <Users size={13} />{solvedBy}
                    </span>
                    <span title="Добавлено"><Calendar size={13} />{formatLongDate(task.date)}</span>
                </span>
            </div>

            {task.task.sharedText && <Markdown className={styles.text} source={task.task.sharedText} />}
            <Markdown className={styles.text} source={task.task.condition} />

            {answerShown && (
                <div className={styles.solution} id={`solution-${task.id}`}>
                    <p className={styles.solutionTitle}><Lightbulb size={14} />Решение</p>
                    {task.reveal.solution && <Markdown className={styles.solutionText} source={task.reveal.solution} />}
                    <p className={styles.solutionAnswer}>Ответ: <b><MathText text={task.reveal.correctAnswer} /></b></p>
                </div>
            )}

            <div className={styles.foot}>
                <button
                    type="button"
                    className={styles.linkBtn}
                    aria-expanded={answerShown}
                    aria-controls={`solution-${task.id}`}
                    onClick={() => setAnswerShown(!answerShown)}
                >
                    {answerShown ? <EyeOff size={16} /> : <Eye size={16} />}
                    <span>{answerShown ? 'Скрыть ответ и решение' : 'Показать ответ и решение'}</span>
                </button>
                <button
                    type="button"
                    className={styles.mark}
                    aria-pressed={solved}
                    disabled={task.autoSolved}
                    title={task.autoSolved ? 'Решено: вы уже ответили на это задание верно' : undefined}
                    onClick={onToggleSolved}
                >
                    {solved ? <CircleCheck size={17} /> : <Circle size={17} />}
                    <span>{solved ? 'Решено' : 'Отметить решённым'}</span>
                </button>
            </div>
        </li>
    );
};
