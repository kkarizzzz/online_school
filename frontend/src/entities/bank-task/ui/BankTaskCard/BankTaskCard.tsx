import { Calendar, Circle, CircleCheck, Eye, EyeOff, Lightbulb, Users } from 'lucide-react';
import { useState, type JSX } from 'react';
import { formatAnswer } from '../../../exam-task';
import { cn, formatLongDate, plural } from '../../../../shared/lib';
import { MathText } from '../../../../shared/ui';
import { LevelMeter } from '../LevelMeter/LevelMeter';
import styles from './BankTaskCard.module.css';
import type { BankTaskCardProps } from './BankTaskCard.props';


/** Задание банка: код, тема, сложность, условие, ответ с решением по кнопке и отметка «решено» */
export const BankTaskCard = ({ task, code, topicName, solved, onToggleSolved }: BankTaskCardProps): JSX.Element => {
    const [answerShown, setAnswerShown] = useState(false);
    const solvedBy = task.solved.toLocaleString('ru-RU');

    return (
        <li className={cn('glass', styles.task, { [styles.isSolved]: solved })}>
            <div className={styles.head}>
                <span className={styles.code}>{code}</span>
                <span className={styles.topic}>{topicName}</span>
                <LevelMeter level={task.level} />
                <span className={styles.facts}>
                    <span title={`Решили ${solvedBy} ${plural(task.solved, 'ученик', 'ученика', 'учеников')}`}>
                        <Users size={13} />{solvedBy}
                    </span>
                    <span title="Добавлено"><Calendar size={13} />{formatLongDate(task.date)}</span>
                </span>
            </div>

            <MathText className={styles.text} text={task.text} />

            {answerShown && (
                <div className={styles.solution} id={`solution-${task.id}`}>
                    <p className={styles.solutionTitle}><Lightbulb size={14} />Решение</p>
                    <MathText className={styles.solutionText} text={task.solution} />
                    <p className={styles.solutionAnswer}>Ответ: <b>{formatAnswer(task.answer)}</b></p>
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
                <button type="button" className={styles.mark} aria-pressed={solved} onClick={onToggleSolved}>
                    {solved ? <CircleCheck size={17} /> : <Circle size={17} />}
                    <span>{solved ? 'Решено' : 'Отметить решённым'}</span>
                </button>
            </div>
        </li>
    );
};
