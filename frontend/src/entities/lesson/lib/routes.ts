export const lessonRoute = (lessonId: string): string =>
    `/profile/learning/theory/lesson/${encodeURIComponent(lessonId)}`;
