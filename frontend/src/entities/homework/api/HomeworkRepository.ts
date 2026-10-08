import type { HomeworkDto, HomeworkResult, HomeworkSession } from '../model/types';

export interface HomeworkRepository {
    /** Все ДЗ ученика с его прогрессом */
    getAll(): Promise<HomeworkDto[]>;
    /** Сохранить начатое ДЗ — после каждого ответа */
    saveSession(id: string, session: HomeworkSession): Promise<void>;
    /** Сдать ДЗ: результат сохраняется, начатое удаляется. Сданное переписать нельзя */
    submit(id: string, result: HomeworkResult): Promise<void>;
}
