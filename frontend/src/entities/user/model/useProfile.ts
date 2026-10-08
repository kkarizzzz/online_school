import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { getProfile, updateMe } from "../api/user.api"
import type { UserUpdate } from "./types"


/** Класс, год ЕГЭ и подключённые предметы текущего пользователя */
export const useUserProfile = () =>
    useQuery({
        queryKey: ['user', 'profile'],
        queryFn: getProfile,
        staleTime: 1000 * 60 * 5,
    })


/** Сохранить имя — данные пользователя в кэше сразу обновляются ответом сервера */
export const useUpdateUser = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (data: UserUpdate) => updateMe(data),
        onSuccess: (user) => queryClient.setQueryData(['user'], user),
    })
}
