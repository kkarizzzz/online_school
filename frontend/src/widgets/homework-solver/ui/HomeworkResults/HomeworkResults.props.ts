import type { Homework, HomeworkResult } from '../../../../entities/homework';

export interface HomeworkResultsProps {
    homework: Homework;
    result: HomeworkResult;
    /** Только что сдано — иначе открыт разбор сданного раньше */
    justFinished?: boolean;
}
