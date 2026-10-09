import {
  Atom,
  BarChart3,
  BookOpen,
  ClipboardList,
  FolderOpen, Home, Layers, Repeat,
  Settings,
  Sigma,
  Terminal,
  Zap
} from 'lucide-react';
import type { NavItem } from '../config';

export const PROFILE_DASHBOARD_CARDS = [
  {
    title: "Обучение",
    description: "Курсы, уроки и домашние задания",
    icon: BookOpen,
    href: "learning",
  },
  {
    title: "Статистика",
    description: "Прогресс, оценки и аналитика",
    icon: BarChart3,
    href: "statistics",
  },
  {
    title: "Настройки",
    description: "Профиль и параметры аккаунта",
    icon: Settings,
    href: "settings",
  },
];


export const PROFILE_NAV_ITEMS: NavItem[] = [
  { 
    id: 'main', 
    href: '/profile/learning', 
    label: 'Главная', 
    icon: Home,
    description: 'Продолжайте с того места, где остановились. Сегодня отличный день, чтобы приблизиться к цели.'
  },
  { 
    id: 'theory', 
    href: '/profile/learning/theory', 
    label: 'Теория', 
    icon: BookOpen,
    description: 'Вся программа от дробей до задачи №19 — в одном маршруте. Темы идут от базы к профилю, пройденные уроки отмечаются сами — вы всегда видите, что дальше.'
  },
  { 
    id: 'homework', 
    href: '/profile/learning/homework', 
    label: 'Домашнее задание', 
    icon: ClipboardList, 
    description: 'Отслеживайте дедлайны и приступайте к заданиям в один клик.',
  },
  { 
    id: 'task-bank', 
    href: '/profile/learning/task-bank', 
    label: 'Банк заданий', 
    icon: Layers,
    description: 'Тренируйтесь по номерам заданий ЕГЭ. Выбирайте тему и нарабатывайте навык.' 
  },
  { 
    id: 'practice', 
    href: '/profile/learning/practice', 
    label: 'Нарешка', 
    icon: Zap,
    description: 'Бесконечная лента задач: «Торнадо» по номерам первой части или персональный режим — свои номера, подтемы и сложность.'
  },
  { 
    id: 'variants', 
    href: '/profile/learning/variants', 
    label: 'Каталог вариантов', 
    icon: FolderOpen,
    description: 'Полные варианты как на ЕГЭ и отработки отдельных номеров. Зачётная — первая попытка: она идёт в статистику пробников.' 
  },
  { 
    id: 'quick-review', 
    href: '/profile/learning/quick-review', 
    label: 'Быстрое повторение', 
    icon: Repeat,
    description: 'Короткие вопросы по формулам, определениям и простым вычислениям. Выберите вариант — сразу увидите, верно ли. Ошибки вернутся через пару вопросов.' 
  },
];

export const SUBJECTS = [
    { id: 'math', label: 'Математика', icon: Sigma },
    { id: 'physics', label: 'Физика', icon: Atom },
    { id: 'informatics', label: 'Информатика', icon: Terminal },
    { id: 'russian', label: 'Русский язык', icon: BookOpen },
];