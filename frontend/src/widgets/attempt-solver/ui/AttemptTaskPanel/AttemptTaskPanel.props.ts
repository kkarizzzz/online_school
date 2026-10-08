import type { AttemptSession } from '../../model/AttemptSession';

export interface AttemptTaskPanelProps {
    session: AttemptSession;
    /** «К сдаче» на последнем задании */
    onSubmit: () => void;
}
