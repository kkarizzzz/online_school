type Listener = () => void;

/**
 * Базовый класс модели с подпиской на изменения.
 * Наследник меняет своё состояние и вызывает notify(), а React-компоненты
 * подписываются через useObservable и перерисовываются по номеру версии.
 */
export abstract class Observable {
    private readonly listeners = new Set<Listener>();
    private version = 0;

    subscribe = (listener: Listener): (() => void) => {
        this.listeners.add(listener);
        return () => {
            this.listeners.delete(listener);
        };
    };

    getVersion = (): number => this.version;

    protected notify(): void {
        this.version += 1;
        this.listeners.forEach((listener) => listener());
    }
}
