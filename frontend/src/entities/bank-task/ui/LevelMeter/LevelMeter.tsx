import { Skull } from 'lucide-react';
import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { BANK_LEVELS } from '../../model/levels';
import styles from './LevelMeter.module.css';
import type { LevelMeterProps } from './LevelMeter.props';


/** Сложность: четыре деления и подпись */
export const LevelMeter = ({ level }: LevelMeterProps): JSX.Element => {
    const { rank, label } = BANK_LEVELS[level];

    return (
        <span className={cn(styles.level, styles[level])} title={`Сложность: ${label}`}>
            <span className={styles.bars} aria-hidden="true">
                {[1, 2, 3, 4].map((i) => <i key={i} className={cn({ [styles.on]: i <= rank })} />)}
            </span>
            {level === 'coffin' && <Skull size={14} className={styles.skull} />}
            {label}
        </span>
    );
};
