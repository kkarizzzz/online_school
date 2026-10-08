import type { HomeworkAttempt } from '../../model/HomeworkAttempt';

export interface HomeworkTaskPanelProps {
    attempt: HomeworkAttempt;
    /** «К сдаче» на последней задаче */
    onSubmit: () => void;
}
