import type { AttemptData } from '../../attempt';
import type { HomeworkList } from '../model/types';

export interface HomeworkRepository {
    /** Все ДЗ ученика с прогрессом и счётчиками вкладок */
    getAll(): Promise<HomeworkList>;
    /** Начать ДЗ, продолжить начатое или открыть разбор сданного — сервер вернёт нужную попытку */
    start(homeworkId: number): Promise<AttemptData>;
}
