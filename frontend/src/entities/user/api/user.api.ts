import { API, apiClient } from "../../../shared/api";
import type { User, UserDto, UserProfile, UserProfileDto, UserUpdate } from "../model/types";


const toUser = (userData: UserDto): User => ({
    id: userData.id,
    firstName: userData.first_name,
    lastName: userData.last_name ?? undefined,
    phoneNumber: userData.phone_number,
    role: userData.role,
});


// 1. Функция проверки пользователя
export const getMe = async (): Promise<User> => {
    const response = await apiClient.get<UserDto>(API.users.me);
    return toUser(response.data);
};


/** Имя и фамилия. Телефон так не меняется */
export const updateMe = async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch<UserDto>(API.users.me, {
        first_name: data.firstName,
        last_name: data.lastName,
    });
    return toUser(response.data);
};


export const getProfile = async (): Promise<UserProfile> => {
    const { data } = await apiClient.get<UserProfileDto>(API.users.profile);
    return {
        grade: data.grade,
        examYear: data.exam_year,
        createdAt: data.created_at,
        subjects: data.subjects.map((s) => ({
            subject: s.subject, targetScore: s.target_score, accessUntil: s.access_until,
        })),
    };
};
