import type { LessonSession } from '../model/LessonSession';

/**
 * После верного ответа — фокус на следующий нерешённый вопрос шага,
 * а если шаг пройден — на кнопку перехода дальше. Ждём кадр, чтобы React успел обновить DOM.
 */
export const focusNextItem = (container: HTMLElement | null, session: LessonSession, stepIndex: number, itemIndex: number): void => {
    requestAnimationFrame(() => {
        if (!container) return;
        const items = session.steps[stepIndex].items;
        for (let j = itemIndex + 1; j < items.length; j++) {
            if (session.progress(stepIndex, j).isResolved) continue;
            const card = container.querySelector<HTMLElement>(`[data-item="${j}"]`);
            card?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card?.querySelector<HTMLElement>('input, button:not([disabled])')?.focus({ preventScroll: true });
            return;
        }
        if (session.isStepDone(stepIndex)) {
            container.querySelector<HTMLElement>('[data-next-step]')?.focus({ preventScroll: true });
        }
    });
};
