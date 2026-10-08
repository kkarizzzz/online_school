export const VARIANTS_ROUTE = '/profile/learning/variants';

/** Начать вариант или продолжить незаконченную попытку */
export const variantSolveRoute = (variantId: number): string => `${VARIANTS_ROUTE}/${variantId}`;

/** Разбор сданной попытки */
export const variantAttemptRoute = (attemptId: number): string => `${VARIANTS_ROUTE}/attempts/${attemptId}`;
