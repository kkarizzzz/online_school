import axios from 'axios';
import { API } from './api.helpers';


let accessToken: string | null = null

export const setAccessToken = (token: string | null) => {
    accessToken = token
}

export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },    
})

apiClient.interceptors.request.use((config) => {
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
})

// Одно обновление токена на всех: страница шлёт запросы параллельно, и при истёкшем токене
// каждый получил бы 401 и пошёл обновлять его сам
let refreshing: Promise<string> | null = null

const refreshAccessToken = (): Promise<string> => {
    refreshing ??= axios
        .post(`${import.meta.env.VITE_API_URL}${API.auth.refresh}`, {}, { withCredentials: true })
        .then((response) => response.data.access_token as string)
        .finally(() => {
            refreshing = null
        })
    return refreshing
}

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._isRetry) {
            originalRequest._isRetry = true

            try {
                accessToken = await refreshAccessToken()

                originalRequest.headers.Authorization = `Bearer ${accessToken}`

                return apiClient(originalRequest)
            } catch(refreshError) {
                accessToken = null
                
                window.dispatchEvent(new CustomEvent('auth:unauthorized'));

                return Promise.reject(refreshError)
            }
        } 

        return Promise.reject(error)
    } 
)