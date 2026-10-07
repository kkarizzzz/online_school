import { PencilLine } from 'lucide-react';
import type { JSX } from 'react';
import { pluralize } from '../../../../shared/lib';
import { ItemCard } from '../ItemCard/ItemCard';
import styles from './PracticeStepView.module.css';
import type { PracticeStepViewProps } from './PracticeStepView.props';


export const PracticeStepView = ({ session, step, stepIndex, onSolved }: PracticeStepViewProps): JSX.Element => (
    <>
        <article className={styles.head}>
            <span className={styles.icon}><PencilLine size={22} /></span>
            <div>
                <p className={styles.kicker}>Практика &middot; {pluralize(step.items.length, 'задача', 'задачи', 'задач')}</p>
                <h2 className={styles.title}>{step.title}</h2>
                <p className={styles.intro}>{step.intro}</p>
            </div>
        </article>

        <section className={styles.tasks}>
            {step.items.map((_, ii) => (
                <ItemCard key={ii} session={session} stepIndex={stepIndex} itemIndex={ii} onSolved={onSolved} />
            ))}
        </section>
    </>
);
