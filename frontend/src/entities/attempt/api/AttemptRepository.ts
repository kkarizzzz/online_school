import type { TaskAttachment } from '../../exam-task';
import type { AttemptData } from '../model/types';

export interface AttemptRepository {
    get(attemptId: number): Promise<AttemptData>;
    /** Черновик ответа — проверяется только при сдаче */
    saveAnswer(attemptId: number, taskId: number, answer: string): Promise<void>;
    /** Открытое задание и время в работе — чтобы продолжить с того же места */
    savePosition(attemptId: number, position: number, timeSpentSec: number): Promise<void>;
    /** Фото решения второй части */
    uploadFile(attemptId: number, taskId: number, file: File): Promise<TaskAttachment>;
    submit(attemptId: number): Promise<AttemptData>;
    /** Бросить вариант (ДЗ бросить нельзя) */
    abandon(attemptId: number): Promise<void>;
}
