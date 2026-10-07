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
    },
    practice: {
        root: '/practice',
    },
} as const;