export const HOMEWORK_LIST_ROUTE = '/profile/learning/homework';

export const homeworkRoute = (homeworkId: number): string => `${HOMEWORK_LIST_ROUTE}/${homeworkId}`;
