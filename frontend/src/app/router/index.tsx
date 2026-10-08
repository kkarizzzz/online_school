import { createBrowserRouter, Outlet } from "react-router";
import { RequireAuth } from "../../features/auth";
import {
    AuthPage, ErrorPage, GraduatesPage, HomePage,
    HomeworkPage, HomeworkSolvePage,
    LearningHomePage, LessonPage, NotFoundPage, ParentsPage,
    PracticePage,
    PricingPage, ProfilePage,
    PsychologistsPage, RepetionQuickPage, SettingsPage, StatisticsPage, TaskBankPage, TaskBankPrototypePage, TeachersPage,
    TheoryPage,
    VariantAttemptPage, VariantSolvePage, VariantsPage
} from "../../pages";
import { LearningLayout, MainLayout, ProfileLayout } from "../layouts";


export const router = createBrowserRouter(
    [
        {
            path: "/",
            element: <MainLayout />,
            errorElement: <ErrorPage />,
            children: [
                { index: true, element: <HomePage />},
                { path: 'pricing', element: <PricingPage />},
                { path: 'teachers', element: <TeachersPage />},
                { path: 'psychologists', element: <PsychologistsPage />},
                { path: 'graduates', element: <GraduatesPage />},
                { path: 'parents', element: <ParentsPage />},
            ],
        },
        {
            path: '/profile',
            element: (
                <RequireAuth>
                    <Outlet />
                </RequireAuth>
            ),
            errorElement: <ErrorPage />,
            children: [
                {
                    element: <ProfileLayout />,
                    children: [
                        { index: true, element: <ProfilePage />}, 
                        { path: 'settings', element: <SettingsPage />},
                        { path: 'statistics', element: <StatisticsPage />},
                    ]
                },
                {
                    path: 'learning', 
                    element: <LearningLayout />,
                    children: [
                        { index: true, element: <LearningHomePage /> }, 
                        { path: 'theory', element: <TheoryPage /> }, 
                        { path: 'theory/lesson/:lessonId', element: <LessonPage /> },
                        { path: 'homework', element: <HomeworkPage /> }, 
                        { path: 'homework/:homeworkId', element: <HomeworkSolvePage /> },
                        { path: 'task-bank', element: <TaskBankPage /> },
                        { path: 'task-bank/:number', element: <TaskBankPrototypePage /> },
                        { path: 'practice', element: <PracticePage /> },
                        { path: 'variants', element: <VariantsPage /> },
                        { path: 'variants/attempts/:attemptId', element: <VariantAttemptPage /> },
                        { path: 'variants/:variantId', element: <VariantSolvePage /> },
                        { path: 'quick-review', element: <RepetionQuickPage /> },
                    ]
                }
            ]
        },
        { 
            path: 'login', 
            errorElement: <ErrorPage />,
            element: <AuthPage mode="login" key="login" />
        },
        { 
            path: 'register', 
            errorElement: <ErrorPage />,
            element: <AuthPage mode="register" key="register" />
        },
        { 
            path: '*', 
            element: <NotFoundPage /> 
        }
    ],
    {
        basename: import.meta.env.BASE_URL,
    }
)