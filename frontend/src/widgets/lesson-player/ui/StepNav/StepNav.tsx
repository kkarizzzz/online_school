import { ArrowLeft, ArrowRight, CircleCheck } from 'lucide-react';
import type { JSX } from 'react';
import { plural } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import styles from './StepNav.module.css';
import type { StepNavProps } from './StepNav.props';


/** Назад / сколько осталось / дальше — под текущим шагом */
export const StepNav = ({ session, onGo }: StepNavProps): JSX.Element => {
    const si = session.current;
    const step = session.steps[si];
    const { done, total } = session.stepCounts(si);
    const isDone = done === total;
    const left = total - done;
    const nextName = si + 1 === session.finishIndex ? 'Завершить урок' : `Дальше: ${session.steps[si + 1].title}`;

    return (
        <nav className={styles.nav}>
            {si > 0
                ? <Button variant="outline" size="m" disableJump onClick={() => onGo(si - 1)}><ArrowLeft size={18} />Назад</Button>
                : <span className={styles.spacer} />}

            {isDone
                ? <span className={styles.noteOk}><CircleCheck size={16} />Шаг пройден</span>
                : <span className={styles.note}>Осталось: {left} {plural(left, ...step.itemWords)} из {total}</span>}

            <Button size="m" disabled={!isDone} data-next-step onClick={() => onGo(si + 1)}>
                {nextName}<ArrowRight size={18} />
            </Button>
        </nav>
    );
};
