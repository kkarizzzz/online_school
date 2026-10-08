import { BookOpenCheck, CheckCircle2, Clock, Flame, Target, Trophy } from "lucide-react";
import type { PsychologistModel, PsychologistNoteModel } from "../../entities/psychologist/model/types";
import PsychologistElena from '../assets/images/psychologist-elena.webp';
import PsychologistMikhail from '../assets/images/psychologist-mikhail.webp';
import PsychologistOlga from '../assets/images/psychologist-olga.webp';
import type { SubjectMetric } from "../config";


// WeeklyActivity component
export const MOCK_DATA_WEEKLY_ACTIVITY = [
    { day: 'Пн', value: 0 },
    { day: 'Вт', value: 0 },
    { day: 'Ср', value: 40 },
    { day: 'Чт', value: 95 },
    { day: 'Пт', value: 100 },
    { day: 'Сб', value: 100 },
    { day: 'Вс', value: 100 },
];


// WidgetMetric component
export const MOCK_WIDGET_METRIC = [
    { id: 'streak', icon: Flame, label: 'Серия', value: '12 дней' },
    { id: 'tasks', icon: Target, label: 'Задач за неделю', value: '48' },
    { id: 'rating', icon: Trophy, label: 'Рейтинг', value: 'Топ 8%' },
];


// UpcomingLessons component
export const MOCK_UPCOMING_LESSONS = [
    { id: 'l2', title: 'Производная сложной функции', moduleNumber: 4, moduleTopic: 'Начала анализа', lessonNumber: 20, lessonTotal: 26, duration: 25 },
    { id: 'l3', title: 'Первообразная и интеграл', moduleNumber: 4, moduleTopic: 'Начала анализа', lessonNumber: 25, lessonTotal: 26, duration: 30 },
    { id: 'l4', title: 'Практикум: задание №11', moduleNumber: 4, moduleTopic: 'Начала анализа', lessonNumber: 26, lessonTotal: 26, duration: 40 },
];


// VariantsPage component
export const MOCK_VARIANTS = [
  {
    title: 'Пробный вариант ЕГЭ №14',
    meta: '18 заданий · профильный уровень',
    rated: true,
    status: 'assigned',
    deadline: 'до 20 июня',
  },
  {
    title: 'Тренировочный вариант №09',
    meta: '18 заданий · профильный уровень',
    rated: false,
    status: 'in-progress',
    deadline: '7 из 18 решено',
  },
  {
    title: 'Досрочный ЕГЭ 2024',
    meta: '18 заданий · официальный',
    rated: true,
    status: 'done',
    score: '82 балла',
    deadline: 'сдано 6 июня',
  },
  {
    title: 'Вариант по стереометрии',
    meta: '12 заданий · тематический',
    rated: false,
    status: 'assigned',
    deadline: 'до 22 июня',
  },
];

// SettingsPage component
export const MOCK_TIERS = [
    { id: 'basic', name: 'Базовый', price: '990 ₽/мес', features: '1 предмет · теория и ДЗ' },
    { id: 'pro', name: 'Профи', price: '2 490 ₽/мес', features: '3 предмета · пробники и психолог' },
    { id: 'premium', name: 'Премиум', price: '3 990 ₽/мес', features: 'Все предметы · личный наставник' },
];

// PsychologistPage component
export const MOCK_CURRENT_PSYCHOLOGIST: PsychologistModel = {
  id: 'elena',
  name: 'Елена Соколова',
  photo: PsychologistElena,
  rating: 4.9,
  reviews: 128,
  bio: 'Клинический психолог, специализация — подростковая мотивация и работа с тревогой перед экзаменами.',
  tags: ['Мотивация', 'Тревожность', 'ЕГЭ'],
};

export const MOCK_PSYCHOLOGIST_NOTES: PsychologistNoteModel[] = [
  {
    id: 1,
    date: '18 августа',
    text: 'Анна, отличная работа на этой неделе! Помни: 15 минут отдыха после каждого часа занятий — это не потеря времени, а инвестиция в концентрацию.',
  },
  {
    id: 2,
    date: '14 августа',
    text: 'Перед пробником сделай дыхательное упражнение 4-7-8. Волнение — это нормально, оно помогает собраться. Ты подготовлена лучше, чем думаешь.',
  },
  {
    id: 3,
    date: '9 августа',
    text: 'Давай на следующей встрече обсудим твой режим сна. Ранний подъём даётся тяжело, попробуем сдвинуть план занятий на вечер.',
  },
];

export const MOCK_AVAILABLE_PSYCHOLOGISTS: PsychologistModel[] = [
  {
    id: 'mikhail',
    name: 'Михаил Верещагин',
    photo: PsychologistMikhail,
    rating: 4.8,
    reviews: 94,
    bio: 'Работаю с прокрастинацией и выгоранием. Помогу выстроить систему, в которой учиться легко и без давления.',
    tags: ['Прокрастинация', 'Выгорание'],
  },
  {
    id: 'olga',
    name: 'Ольга Нестерова',
    photo: PsychologistOlga,
    rating: 5.0,
    reviews: 156,
    bio: 'Специалист по самооценке и уверенности. Вместе научимся спокойно относиться к ошибкам и расти на них.',
    tags: ['Самооценка', 'Уверенность'],
  },
];

// StatisticsPage component
export const MOCK_STAT_METRICS = [
    { icon: Clock, label: 'Часов на платформе', value: '142', delta: '+8 за неделю' },
    { icon: BookOpenCheck, label: 'Просмотрено лекций', value: '87', delta: '+5 за неделю' },
    { icon: CheckCircle2, label: 'Решено задач', value: '1 248', delta: '+96 за неделю' },
    { icon: Flame, label: 'Серия дней', value: '12', delta: 'Личный рекорд' },
];

export const MOCK_SUBJECT_TASKS: SubjectMetric[] = [
    { subject: 'Математика', value: 642, max: 800 },
    { subject: 'Физика', value: 318, max: 500 },
    { subject: 'Информатика', value: 288, max: 400 },
    { subject: 'Русский язык', value: 537, max: 600 },
];

export const MOCK_STATS_ATTENDANCE = [
    { day: 'Пн', value: 2.5 },
    { day: 'Вт', value: 3.2 },
    { day: 'Ср', value: 1.4 },
    { day: 'Чт', value: 4.1 },
    { day: 'Пт', value: 2.8 },
    { day: 'Сб', value: 5.0 },
    { day: 'Вс', value: 1.2 },
];

export const MOCK_EXAMS: SubjectMetric[] = [
    { subject: 'Математика', value: 82, max: 100 },
    { subject: 'Физика', value: 71, max: 100 },
    { subject: 'Информатика', value: 90, max: 100 },
    { subject: 'Русский язык', value: 87, max: 100 },
];
