/**
 * Типизированная запись в localStorage. Ошибки (приватный режим, переполнение,
 * испорченный JSON) не пробрасываются: чтение вернёт null, запись просто не случится.
 */
export class JsonStorage<T> {
    private readonly key: string;

    constructor(key: string) {
        this.key = key;
    }

    read(): T | null {
        try {
            const raw = localStorage.getItem(this.key);
            return raw === null ? null : (JSON.parse(raw) as T);
        } catch {
            return null;
        }
    }

    write(value: T): void {
        try {
            localStorage.setItem(this.key, JSON.stringify(value));
        } catch {
            /* приватный режим — данные просто не сохранятся */
        }
    }

    remove(): void {
        try {
            localStorage.removeItem(this.key);
        } catch {
            /* приватный режим */
        }
    }
}
