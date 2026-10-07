import { Check, Flag } from 'lucide-react';
import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { stepIcon } from '../../lib/stepIcon';
import styles from './StepTrack.module.css';
import type { StepTrackProps } from './StepTrack.props';


/** Шкала шагов урока над сценой */
export const StepTrack = ({ session, onGo, className, ...props }: StepTrackProps): JSX.Element => {
    const indexes = [...session.steps.keys(), session.finishIndex];

    return (
        <ol className={cn(styles.track, className)} aria-label="Шаги урока" {...props}>
            {indexes.map((si) => {
                const isFinish = si === session.finishIndex;
                const step = session.steps[si];
                const done = session.isStepDone(si);
                const current = si === session.current;
                const Icon = done && !current ? Check : isFinish ? Flag : stepIcon(step);

                return (
                    <li
                        key={si}
                        className={cn(styles.step, {
                            [styles.done]: done,
                            [styles.current]: current,
                            [styles.strong]: isFinish || step.kind === 'practice',
                        })}
                    >
                        <button
                            type="button"
                            disabled={!session.isReachable(si)}
                            aria-current={current ? 'step' : undefined}
                            title={isFinish ? 'Итог урока' : step.title}
                            onClick={() => onGo(si)}
                        >
                            <Icon size={16} />
                            <span>{session.stepLabel(si)}</span>
                        </button>
                    </li>
                );
            })}
        </ol>
    );
};
