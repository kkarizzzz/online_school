export const API = {
    auth: {
        sendCode: 'auth/send-code',
        login: 'auth/login',
        register: 'auth/register',
        refresh: '/auth/refresh',
        logout: '/auth/logout',
    },
    users: {
        me: '/users/me',
        profile: '/users/me/profile',
    },
    practice: {
        root: '/practice',
    },
    bank: {
        numbers: '/bank/numbers',
        number: (n: number) => `/bank/numbers/${n}`,
        mark: (taskId: number) => `/bank/tasks/${taskId}/mark`,
    },
    homework: {
        list: '/homework',
        start: (id: number) => `/homework/${id}/start`,
    },
    variants: {
        list: '/variants',
        one: (id: number) => `/variants/${id}`,
        start: (id: number) => `/variants/${id}/start`,
    },
    attempts: {
        one: (id: number) => `/attempts/${id}`,
        answer: (id: number, taskId: number) => `/attempts/${id}/answers/${taskId}`,
        files: (id: number, taskId: number) => `/attempts/${id}/answers/${taskId}/files`,
        position: (id: number) => `/attempts/${id}/position`,
        submit: (id: number) => `/attempts/${id}/submit`,
        abandon: (id: number) => `/attempts/${id}/abandon`,
    },
    stats: {
        me: '/stats/me',
        topics: '/stats/me/topics',
    },
    notifications: {
        list: '/notifications',
        unread: '/notifications/unread-count',
        read: '/notifications/read',
    },
    curriculum: '/curriculum',
    lessons: {
        one: (id: string) => `/lessons/${encodeURIComponent(id)}`,
        complete: (id: string) => `/lessons/${encodeURIComponent(id)}/complete`,
    },
    review: {
        questions: '/review/questions',
        sessions: '/review/sessions',
        session: (id: number) => `/review/sessions/${id}`,
    },
} as const;
