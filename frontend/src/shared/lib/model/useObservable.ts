import { useSyncExternalStore } from 'react';
import type { Observable } from './Observable';

/** Перерисовывает компонент при каждом notify() модели и возвращает её же */
export const useObservable = <T extends Observable>(model: T): T => {
    useSyncExternalStore(model.subscribe, model.getVersion);
    return model;
};
