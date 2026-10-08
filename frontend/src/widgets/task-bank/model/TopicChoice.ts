import type { BankNumber } from '../../../entities/bank-task';

/**
 * Выбранные темы номера в панели тем — запоминаются до закрытия вкладки (sessionStorage).
 * По умолчанию выбраны все.
 */
export class TopicChoice {
    private static key = (n: number) => `bank:topics:${n}`;

    static load(number: BankNumber): Set<string> {
        try {
            const saved: unknown = JSON.parse(sessionStorage.getItem(TopicChoice.key(number.n)) ?? 'null');
            const ids = Array.isArray(saved) ? saved.filter((id) => number.topics.some((t) => t.id === id)) : [];
            if (ids.length) return new Set(ids);
        } catch {
            /* приватный режим */
        }
        return new Set(number.topics.map((t) => t.id));
    }

    static save(number: BankNumber, chosen: ReadonlySet<string>): void {
        try {
            sessionStorage.setItem(TopicChoice.key(number.n), JSON.stringify([...chosen]));
        } catch {
            /* приватный режим */
        }
    }
}
