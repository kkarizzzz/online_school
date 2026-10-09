import { useMemo } from 'react';
import type { Difficulty } from '../../../entities/practice-task';
import { useUser } from '../../../entities/user';
import { JsonStorage } from '../../../shared/lib';
import { ALL_DIFFICULTIES, difficultyFilter, type PracticeScope } from './scope';

/** Персональная подборка: темы и сложности */
export interface PersonalSelection {
    topicIds: number[];
    difficulties: Difficulty[];
}

/** Запущенная подборка — для блока «Последние подборки» */
export interface RecentSelection extends PersonalSelection {
    at: number;
}

const RECENT_LIMIT = 3;

const sameIds = (a: number[], b: number[]): boolean =>
    a.length === b.length && [...a].sort().join() === [...b].sort().join();

const sameSelection = (a: PersonalSelection, b: PersonalSelection): boolean =>
    sameIds(a.topicIds, b.topicIds) && sameIds(difficultyFilter(a.difficulties), difficultyFilter(b.difficulties));

/**
 * Персональный режим в localStorage, отдельно для каждого ученика:
 * текущая подборка и три последние запущенные. Сервер о них не знает — лента получает темы и сложности в запросе.
 */
export class PersonalStorage {
    private readonly selection: JsonStorage<PersonalSelection>;
    private readonly recentList: JsonStorage<RecentSelection[]>;

    constructor(userId: number | string) {
        this.selection = new JsonStorage(`practice:personal:${userId}`);
        this.recentList = new JsonStorage(`practice:recent:${userId}`);
    }

    read(): PersonalSelection {
        const saved = this.selection.read();
        const difficulties = (saved?.difficulties ?? []).filter((d) => ALL_DIFFICULTIES.includes(d));
        return {
            topicIds: saved?.topicIds ?? [],
            difficulties: difficulties.length ? difficulties : ALL_DIFFICULTIES,
        };
    }

    write(selection: PersonalSelection): void {
        this.selection.write(selection);
    }

    scope(): PracticeScope {
        return { kind: 'personal', ...this.read() };
    }

    recent(): RecentSelection[] {
        return (this.recentList.read() ?? []).filter((r) => r.topicIds?.length);
    }

    /** Подборку запустили: она поднимается наверх списка, такая же старая — убирается */
    pushRecent(selection: PersonalSelection): void {
        const item: RecentSelection = { topicIds: selection.topicIds, difficulties: selection.difficulties, at: Date.now() };
        this.recentList.write([item, ...this.recent().filter((r) => !sameSelection(r, item))].slice(0, RECENT_LIMIT));
    }

    isCurrent(selection: PersonalSelection): boolean {
        return sameSelection(selection, this.read());
    }
}

/** Хранилище персонального режима текущего ученика */
export const usePersonalStorage = (): PersonalStorage => {
    const { data: user } = useUser();
    return useMemo(() => new PersonalStorage(user?.id ?? 'guest'), [user?.id]);
};
