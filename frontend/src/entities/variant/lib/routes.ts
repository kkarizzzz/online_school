export const VARIANTS_ROUTE = '/profile/learning/variants';

/** Стартовая страница варианта: правила и «Приступить к варианту» */
export const variantSolveRoute = (variantId: number): string => `${VARIANTS_ROUTE}/${variantId}`;

/** Разбор сданной попытки */
export const variantAttemptRoute = (attemptId: number): string => `${VARIANTS_ROUTE}/attempts/${attemptId}`;
