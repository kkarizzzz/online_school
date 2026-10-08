export const HOMEWORK_LIST_ROUTE = '/profile/learning/homework';

export const homeworkRoute = (homeworkId: string): string =>
    `${HOMEWORK_LIST_ROUTE}/${encodeURIComponent(homeworkId)}`;
