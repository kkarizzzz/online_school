import type { AttemptSession } from '../../model/AttemptSession';

export interface AttemptTaskPanelProps {
    session: AttemptSession;
    /** «К сдаче» на последнем задании */
    onSubmit: () => void;
    /** Можно уйти и вернуться к попытке позже (ДЗ); у вариантов — нельзя */
    resumable?: boolean;
}
