export type Role = 'student' | 'parent'

export type User = {
    id: number;
    firstName: string;
    lastName?: string;
    phoneNumber: string;
    role: Role | 'teacher' | 'admin';
}

export type UserDto = {
    id: number;
    first_name: string;
    last_name?: string | null;
    phone_number: string;
    role: Role | 'teacher' | 'admin';
}

export interface SubjectAccess {
    subject: string;
    targetScore: number | null;
    /** До какого числа оплачен доступ; null — без срока */
    accessUntil: string | null;
}

/** Подробности для кабинета: класс, год ЕГЭ, подключённые предметы */
export interface UserProfile {
    grade: number | null;
    examYear: number | null;
    createdAt: string;
    subjects: SubjectAccess[];
}

export interface UserProfileDto {
    grade: number | null;
    exam_year: number | null;
    created_at: string;
    subjects: { subject: string; target_score: number | null; access_until: string | null }[];
}

export interface UserUpdate {
    firstName?: string;
    lastName?: string | null;
}
